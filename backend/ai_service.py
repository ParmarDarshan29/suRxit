import openai
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class MedLMService:
    """
    AI service for medical analysis using OpenAI GPT or other medical AI models
    In production, this would connect to specialized medical AI like MedLM
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
        # Medical knowledge base for drug interactions
        self.drug_interaction_db = {
            ("warfarin", "aspirin"): {
                "severity": "high",
                "mechanism": "Additive anticoagulant effects",
                "clinical_effects": "Increased bleeding risk",
                "management": "Monitor INR closely, consider alternative therapy"
            },
            ("lisinopril", "nsaids"): {
                "severity": "moderate", 
                "mechanism": "NSAIDs reduce ACE inhibitor effectiveness",
                "clinical_effects": "Reduced blood pressure control, kidney dysfunction",
                "management": "Monitor blood pressure and kidney function"
            },
            ("metformin", "contrast_dye"): {
                "severity": "high",
                "mechanism": "Risk of lactic acidosis with kidney dysfunction",
                "clinical_effects": "Lactic acidosis",
                "management": "Hold metformin 48 hours before and after contrast"
            }
        }
        
        # Drug-food interactions
        self.food_interaction_db = {
            "warfarin": [
                {
                    "food": "Leafy greens (spinach, kale)",
                    "interaction_type": "Vitamin K interaction",
                    "severity": "moderate",
                    "recommendation": "Maintain consistent intake"
                }
            ],
            "grapefruit": [
                {
                    "drug": "Statins",
                    "interaction_type": "CYP3A4 inhibition",
                    "severity": "moderate",
                    "recommendation": "Avoid grapefruit juice"
                }
            ]
        }

    async def analyze_prescription(self, prescription_text: str, patient_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze prescription for drug interactions, adverse reactions, and recommendations
        """
        try:
            # Extract drugs from prescription text
            extracted_drugs = self._extract_drugs(prescription_text)
            
            # Analyze drug-drug interactions
            ddi_interactions = self._analyze_drug_interactions(extracted_drugs)
            
            # Analyze adverse reactions
            adr_reactions = self._analyze_adverse_reactions(extracted_drugs, patient_data)
            
            # Analyze drug-food interactions
            dfi_interactions = self._analyze_food_interactions(extracted_drugs)
            
            # Generate home remedy suggestions
            home_remedies = self._suggest_home_remedies(extracted_drugs)
            
            # Generate safety alerts
            alerts = self._generate_alerts(extracted_drugs, patient_data, ddi_interactions)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(extracted_drugs, patient_data)
            
            return {
                "extracted_drugs": extracted_drugs,
                "drug_interactions": ddi_interactions,
                "adverse_reactions": adr_reactions,
                "food_interactions": dfi_interactions,
                "home_remedies": home_remedies,
                "alerts": alerts,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Prescription analysis failed: {str(e)}")

    async def get_chat_response(self, message: str, context: List[Dict], user_role: str = "doctor") -> Dict[str, Any]:
        """
        Get AI response for medical chat queries
        """
        try:
            # Prepare system prompt based on user role
            system_prompt = self._get_system_prompt(user_role)
            
            # If OpenAI API is available, use it
            if self.api_key:
                response = await self._get_openai_response(message, context, system_prompt)
            else:
                response = await self._get_mock_response(message, user_role)
            
            return {
                "content": response["content"],
                "confidence": response.get("confidence", 0.85),
                "sources": response.get("sources", ["Clinical guidelines", "Drug database"]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Chat service error: {str(e)}")

    def _extract_drugs(self, prescription_text: str) -> List[str]:
        """Extract drug names from prescription text"""
        # Common drug patterns (in production, use NLP/NER models)
        common_drugs = [
            "lisinopril", "metformin", "warfarin", "aspirin", "atorvastatin",
            "omeprazole", "metoprolol", "amlodipine", "losartan", "hydrochlorothiazide",
            "simvastatin", "levothyroxine", "gabapentin", "furosemide", "prednisone"
        ]
        
        found_drugs = []
        text_lower = prescription_text.lower()
        
        for drug in common_drugs:
            if drug in text_lower:
                found_drugs.append(drug.title())
        
        return found_drugs

    def _analyze_drug_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Analyze drug-drug interactions"""
        interactions = []
        
        for i, drug1 in enumerate(drugs):
            for drug2 in drugs[i+1:]:
                key = (drug1.lower(), drug2.lower())
                reverse_key = (drug2.lower(), drug1.lower())
                
                interaction = self.drug_interaction_db.get(key) or self.drug_interaction_db.get(reverse_key)
                
                if interaction:
                    interactions.append({
                        "drug1": drug1,
                        "drug2": drug2,
                        "severity": interaction["severity"],
                        "mechanism": interaction["mechanism"],
                        "clinical_effects": interaction["clinical_effects"],
                        "management": interaction["management"]
                    })
        
        return interactions

    def _analyze_adverse_reactions(self, drugs: List[str], patient_data: Optional[Dict]) -> List[Dict[str, Any]]:
        """Analyze potential adverse drug reactions"""
        reactions = []
        
        # Common ADRs by drug
        adr_database = {
            "metformin": [
                {
                    "reaction": "Gastrointestinal upset",
                    "frequency": "Common (>10%)",
                    "severity": "mild",
                    "management": "Take with food, start with low dose"
                }
            ],
            "lisinopril": [
                {
                    "reaction": "Dry cough",
                    "frequency": "Common (10-15%)",
                    "severity": "mild",
                    "management": "Consider ARB if persistent"
                }
            ],
            "warfarin": [
                {
                    "reaction": "Bleeding",
                    "frequency": "Variable",
                    "severity": "severe",
                    "management": "Regular INR monitoring required"
                }
            ]
        }
        
        for drug in drugs:
            drug_reactions = adr_database.get(drug.lower(), [])
            for reaction in drug_reactions:
                reactions.append({
                    "drug": drug,
                    **reaction
                })
        
        return reactions

    def _analyze_food_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Analyze drug-food interactions"""
        interactions = []
        
        for drug in drugs:
            drug_interactions = self.food_interaction_db.get(drug.lower(), [])
            for interaction in drug_interactions:
                interactions.append({
                    "drug": drug,
                    **interaction
                })
        
        return interactions

    def _suggest_home_remedies(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Suggest complementary home remedies"""
        remedies = [
            {
                "name": "Ginger Tea",
                "indication": "Nausea and digestive upset",
                "preparation": "Steep 1-2g fresh ginger in hot water for 10 minutes",
                "precautions": "Avoid if taking blood thinners",
                "evidence_level": "Moderate - multiple clinical studies"
            },
            {
                "name": "Chamomile Tea", 
                "indication": "Anxiety and sleep disorders",
                "preparation": "Steep 2-3g dried flowers in hot water for 5-10 minutes",
                "precautions": "May interact with warfarin",
                "evidence_level": "Limited - some clinical evidence"
            },
            {
                "name": "Turmeric",
                "indication": "Anti-inflammatory effects",
                "preparation": "500mg curcumin extract daily with meals",
                "precautions": "May increase bleeding risk",
                "evidence_level": "Moderate - clinical trials available"
            }
        ]
        
        return remedies

    def _generate_alerts(self, drugs: List[str], patient_data: Optional[Dict], interactions: List[Dict]) -> List[str]:
        """Generate safety alerts"""
        alerts = []
        
        # High-severity interaction alerts
        for interaction in interactions:
            if interaction["severity"] == "high":
                alerts.append(f"HIGH PRIORITY: {interaction['clinical_effects']} with {interaction['drug1']} and {interaction['drug2']}")
        
        # Patient-specific alerts
        if patient_data:
            allergies = patient_data.get("allergies", [])
            for drug in drugs:
                if any(allergy.lower() in drug.lower() for allergy in allergies):
                    alerts.append(f"ALLERGY ALERT: Patient has documented allergy to {drug}")
        
        return alerts

    def _generate_recommendations(self, drugs: List[str], patient_data: Optional[Dict]) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # Drug-specific recommendations
        drug_recommendations = {
            "metformin": "Take with food to reduce GI side effects",
            "lisinopril": "Monitor blood pressure and kidney function",
            "warfarin": "Regular INR monitoring required",
            "atorvastatin": "Monitor liver function tests"
        }
        
        for drug in drugs:
            rec = drug_recommendations.get(drug.lower())
            if rec:
                recommendations.append(f"{drug}: {rec}")
        
        # General recommendations
        recommendations.extend([
            "Maintain consistent medication timing",
            "Keep updated medication list",
            "Report any new symptoms to healthcare provider"
        ])
        
        return recommendations

    def _get_system_prompt(self, user_role: str) -> str:
        """Get appropriate system prompt based on user role"""
        if user_role == "doctor":
            return """You are a medical AI assistant helping healthcare providers with medication safety. 
            Provide evidence-based information about drug interactions, dosing, and patient care.
            Always recommend consulting clinical guidelines and patient-specific factors."""
        
        elif user_role == "patient":
            return """You are a patient education AI assistant. Provide clear, understandable information
            about medications and health. Always encourage patients to consult their healthcare providers
            for medical decisions. Do not provide specific medical advice."""
        
        else:
            return """You are a medical information assistant. Provide accurate, evidence-based
            information about medications and healthcare topics."""

    async def _get_openai_response(self, message: str, context: List[Dict], system_prompt: str) -> Dict[str, Any]:
        """Get response from OpenAI API"""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context messages
            for msg in context[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            return {
                "content": response.choices[0].message.content,
                "confidence": 0.85,
                "sources": ["OpenAI GPT-3.5", "Medical knowledge base"]
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _get_mock_response(self, message: str, user_role: str) -> Dict[str, Any]:
        """Generate mock response when AI service is unavailable"""
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if "interaction" in message_lower:
            response = "Drug interactions can be serious. I recommend checking for interactions between all medications and consulting your healthcare provider for personalized advice."
        
        elif "side effect" in message_lower:
            response = "Common side effects vary by medication. Monitor for any unusual symptoms and report them to your healthcare provider. Most side effects are mild and manageable."
        
        elif "dosage" in message_lower or "dose" in message_lower:
            response = "Dosing should always be individualized based on patient factors. Follow your healthcare provider's instructions and never adjust doses without medical supervision."
        
        elif "food" in message_lower:
            response = "Some medications have food interactions. Take medications as directed regarding meals, and maintain consistent dietary habits when on medications like warfarin."
        
        else:
            response = "I'm here to help with medication-related questions. For specific medical advice, please consult your healthcare provider or pharmacist."
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "content": response,
            "confidence": 0.75,
            "sources": ["Built-in medical knowledge", "Clinical guidelines"]
        }