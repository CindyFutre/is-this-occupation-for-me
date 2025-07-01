# Homepage User Flow & Structure Diagram

## 🔄 User Journey Flow

```mermaid
graph TD
    A[User Lands on Homepage] --> B{First Time Visitor?}
    B -->|Yes| C[Hero Section - Value Prop]
    B -->|No| D[Quick Search Section]
    
    C --> E[Scroll to Learn More]
    E --> F[Value Proposition Cards]
    F --> G[Social Proof & Testimonials]
    G --> H[How It Works Steps]
    H --> I[Trending Insights]
    I --> J[Final CTA Section]
    
    D --> K[Enter Job Title]
    K --> L[See Popular Suggestions]
    L --> M[Submit Search]
    
    J --> M
    M --> N[Loading State]
    N --> O{Search Results}
    O -->|Success| P[Navigate to Results Page]
    O -->|Suggestions| Q[Show Job Suggestions]
    O -->|Error| R[Show Error Message]
    
    Q --> S[User Selects Suggestion]
    S --> P
    R --> T[Retry Search]
    T --> M
    
    P --> U[View Analysis Results]
    U --> V[Copy Results or New Search]
    V --> A
```

## 📱 Homepage Layout Structure

```mermaid
graph TB
    subgraph "Homepage Layout"
        A[Navigation Bar]
        B[Hero Section]
        C[Smart Search Card]
        D[Value Proposition Grid]
        E[Social Proof Section]
        F[How It Works Steps]
        G[Trending Insights]
        H[Final CTA Section]
        I[Footer]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    
    subgraph "Mobile Adaptations"
        J[Hamburger Menu]
        K[Stacked Hero Layout]
        L[Full-Width Search]
        M[Single Column Grid]
        N[Carousel Testimonials]
        O[Vertical Steps]
        P[Tabbed Insights]
    end
```

## 🎯 Conversion Funnel

```mermaid
funnel
    title Homepage Conversion Funnel
    "Homepage Visitors" : 1000
    "Engage with Content" : 750
    "View Value Props" : 600
    "Interact with Search" : 450
    "Complete Search" : 380
    "View Results" : 320
    "Return Users" : 80
```

## 🧩 Component Hierarchy

```mermaid
graph LR
    subgraph "Page Structure"
        A[HomePage] --> B[HeroSection]
        A --> C[SmartSearchCard]
        A --> D[ValuePropositionGrid]
        A --> E[TestimonialCarousel]
        A --> F[ProcessSteps]
        A --> G[TrendingInsights]
        A --> H[CTASection]
    end
    
    subgraph "shadcn-ui Components"
        I[Card] --> B
        I --> C
        I --> D
        I --> E
        I --> F
        I --> G
        I --> H
        
        J[Button] --> B
        J --> C
        J --> G
        J --> H
        
        K[Input] --> C
        L[Badge] --> C
        L --> G
        
        M[Avatar] --> E
        N[Separator] --> F
        O[Tabs] --> G
    end
```

## 📊 Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant HP as Homepage
    participant API as Backend API
    participant DB as Database
    
    U->>HP: Lands on homepage
    HP->>HP: Load trending data
    HP->>API: GET /trending-insights
    API->>DB: Query popular searches
    DB-->>API: Return trending data
    API-->>HP: Trending insights
    HP-->>U: Display homepage with data
    
    U->>HP: Enters job search
    HP->>API: POST /jobs/analyze
    API->>DB: Query job postings
    DB-->>API: Return analysis
    API-->>HP: Job analysis results
    HP-->>U: Navigate to results page
```

## 🎨 Visual Hierarchy Map

```mermaid
graph TD
    subgraph "Visual Priority Levels"
        A[Level 1: Hero CTA] --> B[Level 2: Search Input]
        B --> C[Level 3: Value Props]
        C --> D[Level 4: Social Proof]
        D --> E[Level 5: Process Steps]
        E --> F[Level 6: Trending Content]
        F --> G[Level 7: Final CTA]
    end
    
    subgraph "Color Coding"
        H[Primary: Deep Blue] --> A
        I[Accent: Bright Blue] --> B
        J[Success: Green] --> C
        K[Warning: Orange] --> D
        L[Neutral: Gray] --> E
        L --> F
        H --> G
    end
```

## 🔄 State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> Loaded
    Loaded --> Searching
    Searching --> SearchSuccess
    Searching --> SearchError
    Searching --> SearchSuggestions
    
    SearchSuccess --> ResultsPage
    SearchError --> Loaded
    SearchSuggestions --> Searching
    
    ResultsPage --> NewSearch
    NewSearch --> Loaded
    
    Loaded --> InteractingWithContent
    InteractingWithContent --> Loaded
    InteractingWithContent --> Searching