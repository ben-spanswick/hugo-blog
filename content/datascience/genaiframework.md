---
title: "Building a Modular GenAI Framework for Document Retrieval and Interaction"
date: 2025-03-21T02:08:37Z
draft: false
categories: ["Artificial Intelligence", "Document Processing"]
tags: ["generative AI", "RAG", "LexRank", "vector databases", "document retrieval", "legal tech"]
description: "A practical guide to building a scalable framework for retrieving and interacting with information from thousands of documents"
---

# **Building a Modular GenAI Framework for Document Retrieval and Interaction**

Without giving too much away, professionally, we're working on a project that has us knee deep in legal documents—thousands upon thousands of pages of contracts, case law, and regulatory filings. Our team was tasked with building a system that could help attorneys quickly find relevant information across this massive corpus and generate accurate, properly cited responses to complex legal questions.

The challenge isn't just the volume of documents. It's the need for precision, attribution, and the ability to synthesize information across multiple sources. Traditional search approaches fell short, and off-the-shelf GenAI solutions can't provide the reliability or citation tracking we needed.

The proposed apporach is a modular framework that combined the best of retrieval augmented generation (RAG), document summarization techniques like LexRank, and agentic models—all designed to be quickly repurposed for different document-heavy domains.

When we finally deployed this system, it should reduce research time for complex legal questions  while maintaining a high accuracy rate compared to expert-generated answers. The key isn't any single technology—it  how we integrated multiple approaches into a cohesive, modular system.

Let's dive into the framework for your own document-intensive use cases.

---

## **The Technology Stack: Beyond Basic RAG**

Before we get into implementation details, let's understand the core technologies that make this framework possible:

### **RAG: The Foundation, Not the Destination**

Retrieval Augmented Generation has become the standard approach for grounding LLMs in external knowledge. But basic RAG implementations—which simply retrieve chunks of text based on vector similarity and feed them to an LLM—have significant limitations when dealing with complex document sets:

- They struggle with multi-hop reasoning across documents
- They often miss important context that's spread across multiple sections
- They provide limited citation capabilities
- They can't effectively prioritize authoritative sources

Our approach uses RAG as a foundation but extends it significantly with additional components.

### **LexRank: The Unsung Hero of Document Summarization**

While everyone talks about RAG, fewer people leverage LexRank—an algorithm that identifies the most representative sentences in a document or collection of documents.

LexRank works by:
1. Creating a graph where sentences are nodes
2. Connecting sentences based on similarity measures
3. Applying a PageRank-like algorithm to identify the most central sentences

What makes LexRank powerful for our use case is that it excels at extractive summarization—pulling out the most important sentences verbatim rather than generating new text. This is crucial for legal and technical domains where precise wording matters.

### **Vector Databases: The Retrieval Engine**

The choice of vector database significantly impacts both performance and capabilities. We evaluated several options:

- **Pinecone:** Excellent performance but limited filtering capabilities
- **Weaviate:** Strong hybrid search but more complex to set up
- **Chroma:** Simple to use but less scalable for very large collections
- **Azure AI Search:** Well-integrated with Azure ecosystem with strong vector search capabilities

For our implementation, we consider Weaviate due to its hybrid search capabilities, which allowes us to combine semantic search with metadata filtering—crucial for narrowing results by date, document type, jurisdiction, and other attributes.

### **Chunking Strategies: The Art of Document Segmentation**

How you divide documents into chunks dramatically affects retrieval quality. Hierarchical chunking approaches typically work best:

1. **Document-level embeddings:** For initial corpus filtering
2. **Section-level chunks:** For main retrieval (typically 500-1000 tokens)
3. **Paragraph-level chunks:** For targeted information extraction
4. **Sentence-level analysis:** For LexRank summarization

This multi-level approach allows the system to zoom in and out as needed, maintaining both broad context and detailed information.

### **Agentic Models: The Orchestrators**

The final piece is an agentic layer that orchestrates the entire process. This layer:
- Interprets user queries
- Determines the optimal retrieval strategy
- Coordinates between retrieval and summarization components
- Formulates responses with proper citations
- Handles follow-up questions with context awareness

We can implement this using a combination of prompt engineering and tool-calling capabilities in models like GPT-4 and Claude 3.

---

## **Building the Document Processing Pipeline**

With our technology stack defined, let's look at how to build the document processing pipeline—the foundation of our framework.

### **Document Ingestion and Preprocessing**

The quality of your document processing directly impacts everything downstream. Our pipeline includes:

1. **Format conversion:** Standardizing all documents to text-based formats
2. **Structure preservation:** Maintaining headings, lists, and paragraph breaks
3. **Metadata extraction:** Pulling out document dates, authors, titles, and other attributes
4. **Entity recognition:** Identifying key entities like organizations, people, and legal citations
5. **Cross-reference detection:** Finding and normalizing references between documents

**Implementation tip:** A combination of Apache Tika for initial conversion, custom Python scripts for structure preservation, and SpaCy for entity recognition. The key is creating a consistent intermediate format that preserves both content and structure.

### **Implementing Hierarchical Chunking**

Rather than using a one-size-fits-all chunking strategy, a hierarchical approach required multiple chunking passes:

```python
def create_hierarchical_chunks(document):
    # Document-level embedding
    doc_embedding = embed_text(document.full_text)
    
    # Section-level chunks (based on headings)
    sections = split_by_headings(document.full_text)
    section_chunks = [
        {
            "text": section,
            "embedding": embed_text(section),
            "metadata": document.metadata
        }
        for section in sections
    ]
    
    # Paragraph-level chunks
    paragraph_chunks = []
    for section in sections:
        paragraphs = split_by_paragraphs(section)
        for paragraph in paragraphs:
            paragraph_chunks.append({
                "text": paragraph,
                "embedding": embed_text(paragraph),
                "metadata": document.metadata,
                "parent_section": section[:100]  # Reference to parent
            })
    
    # Store all levels
    store_chunks(document.id, {
        "document": {"text": document.full_text, "embedding": doc_embedding},
        "sections": section_chunks,
        "paragraphs": paragraph_chunks
    })
```

This approach creates a hierarchical relationship between chunks, allowing the retrieval system to navigate up and down the hierarchy as needed.

### **Data Vetting and Quality Control**

Not all documents are created equal. The proposed implementation includes several data vetting mechanisms:

1. **Duplicate detection:** Identifying and merging duplicate or near-duplicate content
2. **Contradiction detection:** Flagging conflicting information across documents
3. **Recency analysis:** Prioritizing more recent documents when information conflicts
4. **Authority scoring:** Weighting documents based on source authority
5. **Quality filtering:** Removing low-quality or irrelevant documents

**Implementation tip:** Implement a quality scoring system that assigns each document a composite score based on these factors. This score is used both for filtering during ingestion and for ranking during retrieval.

```python
def calculate_quality_score(document):
    scores = {
        "completeness": assess_completeness(document),
        "consistency": check_internal_consistency(document),
        "authority": authority_score(document.metadata["source"]),
        "recency": recency_score(document.metadata["date"]),
        "relevance": domain_relevance_score(document)
    }
    
    # Weighted average
    weights = {"completeness": 0.2, "consistency": 0.2, 
               "authority": 0.3, "recency": 0.2, "relevance": 0.1}
    
    return sum(scores[k] * weights[k] for k in scores)
```

### **Vector Embedding Approaches**

The choice of embedding model significantly impacts retrieval quality:

1. **Domain-specific models outperform general models:** We fine-tuned embeddings on legal text
2. **Larger embedding dimensions improve precision:** We used 1536-dimensional embeddings
3. **Hybrid models combining multiple embeddings perform best:** We ensemble multiple models

For legal documents specifically, the combination of a fine-tuned legal embedding model with a general-purpose model like OpenAI's text-embedding-3-large provided the best results.

---

## **The Retrieval Engine: Finding the Needle in the Haystack**

The next component is the retrieval engine—the system that finds relevant information based on user queries.

### **Vector Database Configuration**

A possible Weaviate configuration includes:

1. **Multiple collections for different chunk sizes:** Document, section, and paragraph levels
2. **Hybrid search configuration:** Combining vector search with BM25 text search
3. **Metadata filtering:** Enabling filtering by document attributes
4. **Cross-references:** Maintaining relationships between chunks

```python
class_obj = {
    "class": "Paragraph",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "text-embedding-3-large",
            "modelVersion": "latest"
        }
    },
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "document_id", "dataType": ["string"]},
        {"name": "section_id", "dataType": ["string"]},
        {"name": "metadata", "dataType": ["object"]},
        {"name": "quality_score", "dataType": ["number"]}
    ]
}
```

### **Multi-Stage Retrieval Process**

Rather than a single retrieval step, we can implemented a multi-stage process:

1. **Query analysis:** Understanding the type of information needed
2. **Corpus filtering:** Using document-level embeddings to narrow the search space
3. **Primary retrieval:** Finding the most relevant sections
4. **Contextual expansion:** Adding related paragraphs for context
5. **Re-ranking:** Applying additional relevance criteria

This multi-stage approach significantly improves precision while maintaining recall.

### **Relevance Scoring Beyond Vector Similarity**

Vector similarity alone isn't enough for complex queries:

1. **Vector similarity:** Semantic relevance to the query
2. **Term overlap:** Keyword matching for precision
3. **Authority score:** Weighting by source reliability
4. **Recency:** Prioritizing newer information when appropriate
5. **Contextual relevance:** How well the chunk fits with other retrieved chunks

```python
def score_chunk(chunk, query, retrieved_chunks):
    # Base vector similarity
    vector_score = vector_similarity(chunk.embedding, query_embedding)
    
    # Term overlap
    term_score = calculate_term_overlap(chunk.text, query)
    
    # Authority from metadata
    authority_score = get_authority_score(chunk.metadata)
    
    # Recency factor
    recency_score = calculate_recency(chunk.metadata.get("date"))
    
    # Contextual relevance to other retrieved chunks
    context_score = calculate_contextual_relevance(chunk, retrieved_chunks)
    
    # Weighted combination
    final_score = (vector_score * 0.4 + 
                  term_score * 0.2 + 
                  authority_score * 0.2 + 
                  recency_score * 0.1 + 
                  context_score * 0.1)
    
    return final_score
```

### **Citation Tracking and Source Attribution**

For domains like legal research, proper citation is critical:

1. **Source documents for all retrieved information**
2. **Specific locations within documents (page, section, paragraph)**
3. **Citation formatting based on domain standards**
4. **Confidence scores for each piece of information**

This enables the system to generate properly cited responses and allows users to verify information directly from source documents.

---

## **The Summarization Layer: From Retrieval to Understanding**

Retrieving relevant chunks is only half the battle. The summarization layer transforms these chunks into coherent, comprehensive answers.

### **LexRank Implementation for Extractive Summarization**

LexRank implementation works in several stages:

1. **Sentence segmentation:** Breaking retrieved chunks into individual sentences
2. **Similarity matrix construction:** Calculating pairwise similarities between sentences
3. **Graph creation:** Building a graph where sentences are nodes and similarities are edges
4. **Centrality calculation:** Applying a modified PageRank algorithm
5. **Sentence selection:** Extracting the most central sentences

```python
def lexrank_summarize(chunks, query, num_sentences=5):
    # Extract all sentences from chunks
    sentences = []
    for chunk in chunks:
        chunk_sentences = split_into_sentences(chunk.text)
        for sentence in chunk_sentences:
            sentences.append({
                "text": sentence,
                "source": chunk.metadata,
                "chunk_id": chunk.id
            })
    
    # Create similarity matrix
    embeddings = [embed_text(s["text"]) for s in sentences]
    similarity_matrix = cosine_similarity(embeddings)
    
    # Apply threshold to create graph
    threshold = 0.3
    for i in range(len(similarity_matrix)):
        for j in range(len(similarity_matrix)):
            if similarity_matrix[i][j] < threshold:
                similarity_matrix[i][j] = 0
    
    # Calculate LexRank scores
    scores = calculate_lexrank_scores(similarity_matrix)
    
    # Select top sentences
    ranked_sentences = [(sentences[i], scores[i]) 
                        for i in range(len(sentences))]
    ranked_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Return top sentences with their sources
    return [rs[0] for rs in ranked_sentences[:num_sentences]]
```

The key advantage of LexRank is that it extracts actual sentences from the documents, preserving the original wording—critical for accuracy in technical and legal domains.

### **Combining RAG with LexRank**

This framework combines RAG and LexRank in a complementary way:

1. **RAG retrieves relevant chunks** based on semantic similarity
2. **LexRank identifies the most representative sentences** within those chunks
3. **The LLM generates a coherent answer** using both the retrieved chunks and the LexRank summary
4. **Citations are maintained throughout** the process

This hybrid approach leverages the strengths of both techniques—RAG's ability to find relevant information and LexRank's ability to identify the most important points.

### **Maintaining Context Across Multiple Documents**

One challenge with complex queries is maintaining context across multiple documents:

1. **Cross-document entity resolution:** Identifying when different documents refer to the same entities
2. **Temporal alignment:** Understanding the chronological relationship between documents
3. **Contradiction detection:** Identifying and resolving conflicting information
4. **Context graphs:** Building relationships between information across documents

This allows the system to synthesize information coherently even when it's spread across multiple sources.

### **Ensuring Factual Accuracy**

To maximize accuracy, this framework includes several verification mechanisms:

1. **Fact verification:** Checking generated content against retrieved chunks
2. **Citation validation:** Ensuring citations actually support the claims
3. **Confidence scoring:** Indicating the system's confidence in each part of the response
4. **Uncertainty highlighting:** Explicitly marking areas where information is ambiguous or conflicting

```python
def verify_response(generated_response, retrieved_chunks):
    # Extract claims from response
    claims = extract_claims(generated_response)
    
    # Verify each claim against retrieved chunks
    verification_results = []
    for claim in claims:
        support = find_supporting_evidence(claim, retrieved_chunks)
        contradictions = find_contradicting_evidence(claim, retrieved_chunks)
        
        verification_results.append({
            "claim": claim,
            "supported": len(support) > 0,
            "support_strength": calculate_support_strength(support),
            "contradicted": len(contradictions) > 0,
            "sources": [s.metadata for s in support]
        })
    
    # Annotate response with verification results
    annotated_response = annotate_response(generated_response, verification_results)
    
    return annotated_response
```

---

## **The Interaction Layer: Making It User-Friendly**

The final component is the interaction layer—the interface between users and the underlying system.

### **Agentic Models for User Interaction**

Implementation of an agentic approach where the model:

1. **Interprets the user's question** to understand intent
2. **Formulates a retrieval strategy** based on the question type
3. **Executes the appropriate retrieval and summarization steps**
4. **Generates a response** with appropriate citations
5. **Maintains conversation context** for follow-up questions

This agent-based approach allows the system to adapt its strategy based on the specific question rather than using a one-size-fits-all approach.

### **Query Understanding and Refinement**

Not all user queries are well-formed:

1. **Query classification:** Identifying the type of question (factual, analytical, comparative)
2. **Query expansion:** Adding relevant terms to improve retrieval
3. **Ambiguity resolution:** Identifying and clarifying ambiguous terms
4. **Decomposition:** Breaking complex questions into simpler sub-questions

```python
def process_query(query, conversation_history=None):
    # Classify query type
    query_type = classify_query(query)
    
    # Expand query based on type
    expanded_query = expand_query(query, query_type)
    
    # Check for ambiguities
    ambiguities = detect_ambiguities(expanded_query)
    if ambiguities and not conversation_history:
        # If this is the first interaction, ask for clarification
        return generate_clarification_request(ambiguities)
    
    # For complex queries, decompose into sub-questions
    if query_type == "complex":
        sub_questions = decompose_query(expanded_query)
        sub_answers = [retrieve_and_generate(sq) for sq in sub_questions]
        return synthesize_answers(sub_answers, query)
    else:
        # Standard retrieval and generation
        return retrieve_and_generate(expanded_query)
```

### **Presenting Results with Citations**

The presentation of results is critical for usability:

1. **Structures responses logically** with clear sections
2. **Includes inline citations** linked to source documents
3. **Provides confidence indicators** for different parts of the response
4. **Offers direct quotes from source documents** for key points
5. **Includes a summary of sources used** at the end

### **Handling Follow-up Questions**

One of the most powerful features is the ability to handle follow-up questions with full context awareness:

1. **Maintaining conversation history** across interactions
2. **Resolving references** to previous questions and answers
3. **Reusing relevant retrievals** from previous questions
4. **Tracking the user's focus** as it shifts during conversation

This creates a much more natural interaction pattern where users can drill down into topics of interest.

---

## **Making It Modular and Scalable**

The key to making this framework reusable across different domains is its modular architecture.

### **Component-Based Architecture**

This framework is built around clearly defined components:

1. **Document Processor:** Handles ingestion and chunking
2. **Embedding Service:** Manages vector embeddings
3. **Retrieval Engine:** Finds relevant information
4. **Summarization Service:** Applies LexRank and other techniques
5. **Response Generator:** Creates the final output
6. **Interaction Manager:** Handles user queries and conversation

Each component has well-defined interfaces, allowing them to be replaced or modified independently.

### **Separation of Concerns**

This modular approach enables clear separation of concerns:

1. **Domain-specific knowledge** is contained in the document corpus
2. **Retrieval logic** is independent of document content
3. **Summarization techniques** can be swapped based on domain needs
4. **Interaction patterns** can be customized for different user types

This makes the framework adaptable to different domains without rewriting core components.

### **Configuration-Driven Customization**

Rather than hardcoding domain-specific logic, we can use configuration files to customize behavior:

```yaml
domain_config:
  name: "legal_research"
  
  # Document processing
  chunking:
    strategy: "hierarchical"
    section_delimiters: ["##", "Section", "Article"]
    max_chunk_size: 1000
    
  # Embedding
  embedding:
    model: "text-embedding-3-large"
    dimensions: 1536
    
  # Retrieval
  retrieval:
    vector_db: "weaviate"
    top_k: 25
    reranking: true
    filters:
      - metadata_field: "jurisdiction"
        required: true
      - metadata_field: "document_type"
        required: false
        
  # Summarization
  summarization:
    primary_method: "lexrank"
    extractive_ratio: 0.7
    min_sentences: 3
    
  # Response generation
  response:
    citation_format: "bluebook"
    include_confidence: true
    max_length: 1000
```

This configuration-driven approach allows quick adaptation to new domains without code changes.

### **Deployment Patterns**

The framework supports several deployment patterns:

1. **Standalone application:** For self-contained deployments
2. **Microservices architecture:** For scalable cloud deployments
3. **Hybrid deployment:** With sensitive components on-premises
4. **Serverless functions:** For cost-effective scaling

This framework can be deployed in both cloud and on-premises environments.

---

## **Implementation Case Study: Legal Document Analysis**

To illustrate the framework in action, let's look at our implementation for a legal research application.

### **The Challenge**

A law firm needed to analyze thousands of contracts, case law documents, and regulatory filings to:
- Identify relevant precedents for specific legal questions
- Extract key clauses and provisions from contracts
- Track regulatory changes affecting client obligations
- Generate properly cited legal memos

### **Implementation Details**

1. **Document Processing:**
   - Specialized legal document parsers for different document types
   - Hierarchical chunking based on legal document structure
   - Entity recognition for legal entities, citations, and provisions

2. **Retrieval Strategy:**
   - Primary focus on authoritative sources
   - Jurisdiction-based filtering
   - Temporal awareness for legal precedents
   - Citation graph analysis

3. **Summarization Approach:**
   - Heavy emphasis on extractive summarization
   - Preservation of exact legal language
   - Structured output following legal memo formats

4. **User Interaction:**
   - Query templates for common legal questions
   - Explicit confidence indicators
   - Full citation tracking
   - Interactive exploration of legal reasoning


### **Lessons Learned**

1. **Domain-specific chunking is critical:** Legal documents required specialized chunking based on their structure
2. **Authority matters more than recency:** Unlike some domains, older but more authoritative sources often take precedence
3. **Citation precision is non-negotiable:** Even small citation errors significantly reduced trust in the system
4. **Explanation is as important as answers:** Attorneys valued the system's ability to explain its reasoning

---

## **Final Thoughts: Building Your Own Framework**

Here are the key takeaways for building your own implementation:

1. **Go beyond basic RAG:** Combine multiple techniques like LexRank for better results
2. **Invest in document processing:** The quality of your chunking and metadata extraction directly impacts everything downstream
3. **Make modularity a priority:** Design for reusability across domains from the start
4. **Focus on attribution:** Proper citation and source tracking builds trust and enables verification
5. **Adapt to your domain:** Customize retrieval and summarization strategies based on domain-specific needs

The most exciting aspect of this approach is its adaptability. Variations of this framework can be deployed across legal, medical, financial, and technical documentation domains—each time adapting the components rather than starting from scratch.

If you're dealing with large document collections and need more than just basic search or generic AI responses, this modular approach combining RAG, LexRank, and agentic models provides a powerful foundation that can be tailored to your specific needs.

The future of document intelligence isn't just about finding information—it's about understanding it, synthesizing it, and presenting it in ways that augment human expertise rather than just attempting to replace it.

---

*This post draws on my experience building document intelligence systems across multiple domains. The approaches outlined here have been implemented in production environments handling millions of documents and thousands of daily queries.*
