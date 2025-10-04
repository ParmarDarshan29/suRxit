# suRxit Architecture# System Architecture



suRxit is built as a set of loosely coupled microservices, each responsible for a distinct stage in the risk intelligence pipeline. This modularity enables scalability, maintainability, and rapid iteration.MedKG-Rx is built as a set of loosely coupled microservices, each responsible for a distinct stage in the clinical document-to-risk pipeline. The architecture ensures scalability, modularity, and compliance with healthcare data standards.



## Microservices Flow## Microservice Flow

1. **OCR**: Converts scanned documents to machine-readable text.
2. **NER**: Extracts medical entities from text.
3. **Standardizer**: Maps entities to standard vocabularies (e.g., SNOMED, RxNorm).
4. **Knowledge Graph**: Links entities and relationships.
5. **FeatureGen**: Generates features for downstream models.
6. **GNN**: Predicts risk using graph neural networks.
7. **Recommender**: Suggests interventions or next steps.
8. **MedLM**: Provides LLM-based explanations.
9. **Risk**: Aggregates and explains risk scores.
10. **API-Gateway**: Orchestrates service calls and enforces security.
11. **Frontend**: Presents results and explanations to clinicians.



## Diagram## Architecture Diagram

```mermaid```mermaid

flowchart LRflowchart LR

    A[OCR] --> B[NER]    A[OCR] --> B[NER]

    B --> C[Standardizer]    B --> C[Standardizer]

    C --> D[Knowledge Graph]    C --> D[KG]

    D --> E[FeatureGen]    D --> E[FeatureGen]

    E --> F[GNN]    E --> F[GNN]

    F --> G[Recommender]    F --> G[Recommender]

    G --> H[MedLM]    G --> H[MedLM]

    H --> I[Risk]    H --> I[Risk]

    I --> J[API-Gateway]    I --> J[API-Gateway]

    J --> K[Frontend]    J --> K[Frontend]

``````

