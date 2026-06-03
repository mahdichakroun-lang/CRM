# Codes PlantUML — Tous les diagrammes du rapport CRM

> [!NOTE]
> 14 diagrammes au total, copiez chaque bloc dans [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/) pour générer le PNG/SVG.

---

## Chapitre 2 — Diagrammes de cas d'utilisation

### 2.7.1 — Cas d'utilisation global

```plantuml
@startuml UC_Global
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle
skinparam shadowing false

rectangle "Système CRM" {
  (S'authentifier) as AUTH
  (Gérer les utilisateurs) as USERS
  (Consulter l'audit) as AUDIT
  (Consulter le dashboard) as DASH
  (Gérer les leads) as LEADS
  (Gérer les comptes) as ACCOUNTS
  (Gérer les contacts) as CONTACTS
  (Gérer les deals) as DEALS
  (Gérer les devis) as QUOTES
  (Enregistrer les activités) as ACTIV
  (Gérer les tickets) as TICKETS
  (Accéder au portail client) as PORTAIL
  (Utiliser l'app mobile) as MOBILE
  (Interroger le chatbot IA) as CHATBOT
}

:Administrateur: as Admin
:Manager: as Manager
:Commercial: as Commercial
:Support: as Support
:Client: as Client

Admin --> AUTH
Admin --> USERS
Admin --> AUDIT
Admin --> DASH

Manager --> AUTH
Manager --> DASH
Manager --> LEADS
Manager --> DEALS

Commercial --> AUTH
Commercial --> LEADS
Commercial --> ACCOUNTS
Commercial --> CONTACTS
Commercial --> DEALS
Commercial --> QUOTES
Commercial --> ACTIV

Support --> AUTH
Support --> TICKETS

Client --> AUTH
Client --> PORTAIL
Client --> MOBILE
Client --> CHATBOT
@enduml
```

### 2.7.2 — Gestion des Leads

```plantuml
@startuml UC_Leads
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle

rectangle "Module Leads" {
  (Créer un lead) as C
  (Modifier un lead) as M
  (Consulter les leads) as CO
  (Filtrer les leads) as F
  (Qualifier un lead) as Q
  (Convertir un lead) as CV
  (Supprimer un lead) as S
  (Créer un compte) as CA
  (Créer un contact) as CC
  (Créer un deal) as CD
}

:Commercial: as Com
:Manager: as Mgr

Com --> C
Com --> M
Com --> CO
Com --> F
Com --> Q
Com --> CV
Com --> S

Mgr --> CO
Mgr --> F

CV ..> CA : <<include>>
CV ..> CC : <<include>>
CV ..> CD : <<include>>
@enduml
```

### 2.7.3 — Gestion des Tickets

```plantuml
@startuml UC_Tickets
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle

rectangle "Module Tickets" {
  (Créer un ticket) as CT
  (Consulter les tickets) as CO
  (Assigner un ticket) as AS
  (Changer le statut) as CS
  (Répondre (message public)) as RP
  (Ajouter une note interne) as NI
  (Clôturer un ticket) as CL
  (Filtrer par priorité / statut) as FI
}

:Client: as Cli
:Support: as Sup
:Manager: as Mgr
:Administrateur: as Adm

Cli --> CT
Cli --> CO
Cli --> RP

Sup --> CO
Sup --> AS
Sup --> CS
Sup --> RP
Sup --> NI
Sup --> CL
Sup --> FI

Mgr --> CO
Mgr --> AS
Mgr --> FI

Adm --> CO
@enduml
```

### 2.7.4 — Portail Client

```plantuml
@startuml UC_Portail
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle

rectangle "Portail Client" {
  (Se connecter) as CON
  (Consulter le dashboard) as DASH
  (Consulter ses tickets) as TK
  (Créer un ticket) as CT
  (Répondre à un ticket) as RT
  (Consulter ses devis) as DV
  (Consulter son profil) as PR
  (Modifier son profil) as MP
  (Interroger le chatbot IA) as CH
}

:Client: as Cli

Cli --> CON
Cli --> DASH
Cli --> TK
Cli --> CT
Cli --> RT
Cli --> DV
Cli --> PR
Cli --> MP
Cli --> CH
@enduml
```

### 2.7.5 — Application Mobile

```plantuml
@startuml UC_Mobile
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle

rectangle "Application Mobile" {
  (S'authentifier) as AUTH
  (Consulter le dashboard) as DASH
  (Consulter ses tickets) as TK
  (Ajouter un message à un ticket) as MSG
  (Consulter ses devis) as DV
  (Gérer son profil) as PR
  (Interroger le chatbot IA) as CH
  (Recevoir un message de blocage) as BL
}

:Client: as Cli
:Utilisateur interne: as Int

Cli --> AUTH
Cli --> DASH
Cli --> TK
Cli --> MSG
Cli --> DV
Cli --> PR
Cli --> CH

Int --> AUTH
Int --> BL
@enduml
```

### 2.7.6 — Chatbot IA (RAG)

```plantuml
@startuml UC_Chatbot
left to right direction
skinparam actorStyle awesome
skinparam packageStyle rectangle

rectangle "Module Chatbot IA (RAG)" {
  (Poser une question\nen langage naturel) as Q
  (Rechercher dans la\nbase documentaire) as R
  (Générer une réponse\ncontextualisée) as G
  (Afficher les sources\nutilisées) as S
  (Gérer le mode dégradé) as D
}

:Utilisateur authentifié: as U
:Système RAG: as RAG

U --> Q
Q ..> R : <<include>>
R ..> G : <<include>>
G ..> S : <<include>>
D ..> G : <<extend>>

RAG --> R
RAG --> G
@enduml
```

---

## Chapitre 3 — Diagramme de classes

### 3.2 — Diagramme de classes du CRM

```plantuml
@startuml ClassDiagram
skinparam classAttributeIconSize 0
skinparam shadowing false
hide circle

class User {
  +id : int
  +name : str
  +email : str
  +hashed_password : str
  +role : UserRole
  +is_active : bool
  +phone : str
  +avatar_url : str
  +account_id : int [FK]
}
enum UserRole {
  admin
  commercial
  support
  manager
  client
}

class Account {
  +id : int
  +name : str
  +sector : str
  +industry : str
  +website : str
  +phone : str
  +email : str
  +address : str
  +city : str
  +country : str
  +notes : str
  +owner_user_id : int [FK]
}

class Contact {
  +id : int
  +account_id : int [FK]
  +first_name : str
  +last_name : str
  +email : str
  +phone : str
  +position : str
  +notes : str
}

class Lead {
  +id : int
  +company_name : str
  +contact_name : str
  +email : str
  +phone : str
  +source : LeadSource
  +status : LeadStatus
  +owner_user_id : int [FK]
  +notes : str
  +estimated_value : int
  +converted_account_id : int [FK]
  +converted_contact_id : int [FK]
  +converted_deal_id : int [FK]
}
enum LeadStatus {
  new
  contacted
  qualified
  unqualified
  converted
}
enum LeadSource {
  website
  phone
  referral
  trade_show
  social_media
  email
  other
}

class Deal {
  +id : int
  +account_id : int [FK]
  +name : str
  +stage : DealStage
  +value : decimal
  +probability : int
  +expected_close_date : date
  +owner_user_id : int [FK]
  +notes : str
  +lost_reason : str
}
enum DealStage {
  qualification
  proposal
  negotiation
  won
  lost
}

class Quote {
  +id : int
  +deal_id : int [FK]
  +reference : str
  +amount : decimal
  +status : QuoteStatus
  +pdf_url : str
  +notes : str
}
enum QuoteStatus {
  draft
  sent
  accepted
  rejected
}

class Ticket {
  +id : int
  +account_id : int [FK]
  +contact_id : int [FK]
  +subject : str
  +description : str
  +category : TicketCategory
  +priority : TicketPriority
  +status : TicketStatus
  +assigned_to : int [FK]
  +created_by : int [FK]
  +due_date : datetime
  +resolved_at : datetime
}
enum TicketStatus {
  open
  in_progress
  waiting_customer
  resolved
  closed
}
enum TicketPriority {
  low
  medium
  high
  urgent
}
enum TicketCategory {
  bug
  feature_request
  support
  question
  incident
  other
}

class TicketMessage {
  +id : int
  +ticket_id : int [FK]
  +author_user_id : int [FK]
  +message : str
  +is_internal : bool
}

class Activity {
  +id : int
  +type : ActivityType
  +subject : str
  +note : str
  +due_date : datetime
  +account_id : int [FK]
  +contact_id : int [FK]
  +deal_id : int [FK]
  +created_by : int [FK]
}
enum ActivityType {
  call
  email
  meeting
  note
}

class AuditLog {
  +id : int
  +actor_user_id : int [FK]
  +entity : str
  +entity_id : int
  +action : str
  +before_json : text
  +after_json : text
  +description : str
}

' ── Relations ──
User "1" --> "0..1" Account : client_account
Account "1" --> "0..1" User : owner
Account "1" *-- "*" Contact
Account "1" *-- "*" Deal
Account "1" *-- "*" Ticket
Deal "1" *-- "*" Quote
Ticket "1" *-- "*" TicketMessage
Lead "0..1" ..> Account : converted
Lead "0..1" ..> Contact : converted
Lead "0..1" ..> Deal : converted
Lead "*" --> "0..1" User : owner
Deal "*" --> "0..1" User : owner
Ticket "*" --> "0..1" User : assignee
Ticket "*" --> "1" User : creator
TicketMessage "*" --> "0..1" User : author
Activity "*" --> "0..1" Account
Activity "*" --> "0..1" Contact
Activity "*" --> "0..1" Deal
Activity "*" --> "0..1" User : creator
AuditLog "*" --> "0..1" User : actor

User ..> UserRole
Lead ..> LeadStatus
Lead ..> LeadSource
Deal ..> DealStage
Quote ..> QuoteStatus
Ticket ..> TicketStatus
Ticket ..> TicketPriority
Ticket ..> TicketCategory
Activity ..> ActivityType
@enduml
```

---

## Chapitre 3 — Diagramme Entité-Relation (ERD)

### 3.3 — ERD de la base CRM

```plantuml
@startuml ERD
!define TABLE(x) entity x << (T, #FFAAAA) >>
skinparam shadowing false
skinparam linetype ortho

TABLE(users) {
  *id : INT <<PK>>
  --
  name : VARCHAR(150)
  email : VARCHAR(255) <<UNIQUE>>
  hashed_password : VARCHAR(255)
  role : ENUM
  is_active : BOOLEAN
  phone : VARCHAR(30)
  avatar_url : VARCHAR(500)
  account_id : INT <<FK>>
}

TABLE(accounts) {
  *id : INT <<PK>>
  --
  name : VARCHAR(255)
  sector : VARCHAR(100)
  industry : VARCHAR(100)
  website : VARCHAR(500)
  phone : VARCHAR(30)
  email : VARCHAR(255)
  address : TEXT
  city : VARCHAR(100)
  country : VARCHAR(100)
  notes : TEXT
  owner_user_id : INT <<FK>>
}

TABLE(contacts) {
  *id : INT <<PK>>
  --
  account_id : INT <<FK>>
  first_name : VARCHAR(100)
  last_name : VARCHAR(100)
  email : VARCHAR(255)
  phone : VARCHAR(30)
  position : VARCHAR(150)
  notes : TEXT
}

TABLE(leads) {
  *id : INT <<PK>>
  --
  company_name : VARCHAR(255)
  contact_name : VARCHAR(255)
  email : VARCHAR(255)
  phone : VARCHAR(30)
  source : ENUM
  status : ENUM
  owner_user_id : INT <<FK>>
  notes : TEXT
  estimated_value : INT
  converted_account_id : INT <<FK>>
  converted_contact_id : INT <<FK>>
  converted_deal_id : INT <<FK>>
}

TABLE(deals) {
  *id : INT <<PK>>
  --
  account_id : INT <<FK>>
  name : VARCHAR(255)
  stage : ENUM
  value : DECIMAL(15,2)
  probability : INT
  expected_close_date : DATE
  owner_user_id : INT <<FK>>
  notes : TEXT
  lost_reason : VARCHAR(500)
}

TABLE(quotes) {
  *id : INT <<PK>>
  --
  deal_id : INT <<FK>>
  reference : VARCHAR(50) <<UNIQUE>>
  amount : DECIMAL(15,2)
  status : ENUM
  pdf_url : VARCHAR(500)
  notes : VARCHAR(1000)
}

TABLE(tickets) {
  *id : INT <<PK>>
  --
  account_id : INT <<FK>>
  contact_id : INT <<FK>>
  subject : VARCHAR(500)
  description : TEXT
  category : ENUM
  priority : ENUM
  status : ENUM
  assigned_to : INT <<FK>>
  created_by : INT <<FK>>
  due_date : DATETIME
  resolved_at : DATETIME
}

TABLE(ticket_messages) {
  *id : INT <<PK>>
  --
  ticket_id : INT <<FK>>
  author_user_id : INT <<FK>>
  message : TEXT
  is_internal : BOOLEAN
}

TABLE(activities) {
  *id : INT <<PK>>
  --
  type : ENUM
  subject : VARCHAR(255)
  note : TEXT
  due_date : DATETIME
  account_id : INT <<FK>>
  contact_id : INT <<FK>>
  deal_id : INT <<FK>>
  created_by : INT <<FK>>
}

TABLE(audit_logs) {
  *id : INT <<PK>>
  --
  actor_user_id : INT <<FK>>
  entity : VARCHAR(100)
  entity_id : INT
  action : VARCHAR(50)
  before_json : TEXT
  after_json : TEXT
  description : VARCHAR(500)
}

users }o--|| accounts : account_id
accounts }o--|| users : owner_user_id
contacts }|--|| accounts : account_id
deals }|--|| accounts : account_id
deals }o--|| users : owner_user_id
quotes }|--|| deals : deal_id
tickets }|--|| accounts : account_id
tickets }o--o| contacts : contact_id
tickets }o--|| users : assigned_to
tickets }|--|| users : created_by
ticket_messages }|--|| tickets : ticket_id
ticket_messages }o--|| users : author_user_id
leads }o--|| users : owner_user_id
leads }o--o| accounts : converted_account_id
leads }o--o| contacts : converted_contact_id
leads }o--o| deals : converted_deal_id
activities }o--o| accounts : account_id
activities }o--o| contacts : contact_id
activities }o--o| deals : deal_id
activities }o--|| users : created_by
audit_logs }o--|| users : actor_user_id
@enduml
```

---

## Chapitre 3 — Diagrammes de séquence

### 3.4.1 — Authentification JWT

```plantuml
@startuml Seq_Auth
skinparam shadowing false
actor Utilisateur as U
participant "Interface\nClient" as UI
participant "API Auth\n/api/v1/auth" as API
participant "AuthService" as SVC
participant "Security\n(JWT + bcrypt)" as SEC
database "MySQL" as DB

U -> UI : Saisir email + mot de passe
UI -> API : POST /auth/login {email, password}
API -> SVC : authenticate(email, password)
SVC -> DB : SELECT user WHERE email = ?
DB --> SVC : User row
SVC -> SEC : verify_password(plain, hashed)
SEC --> SVC : OK
SVC -> SEC : create_access_token(user_id, role)
SEC --> SVC : JWT token
SVC --> API : {access_token, user}
API --> UI : 200 OK + token
UI -> UI : Stocker le token (localStorage / SecureStore)
UI --> U : Redirection selon le rôle

== Appels suivants ==
U -> UI : Action protégée
UI -> API : GET /auth/me\nAuthorization: Bearer <token>
API -> SEC : decode_token(token)
SEC --> API : user_id, role
API -> DB : SELECT user WHERE id = ?
DB --> API : User row
API --> UI : 200 OK + profil
@enduml
```

### 3.4.2 — Conversion d'un Lead

```plantuml
@startuml Seq_Conversion
skinparam shadowing false
actor Commercial as U
participant "Frontend" as UI
participant "API Leads\n/api/v1/leads" as API
participant "LeadService" as LS
participant "AccountRepo" as AR
participant "ContactRepo" as CR
participant "DealRepo" as DR
database "MySQL" as DB

U -> UI : Cliquer "Convertir le lead"
UI -> API : POST /leads/{id}/convert
API -> LS : convert(lead_id)

LS -> DB : SELECT lead WHERE id = ? AND status = 'qualified'
DB --> LS : Lead qualifié

group Transaction
  LS -> AR : create(Account from lead)
  AR -> DB : INSERT INTO accounts
  DB --> AR : account_id
  AR --> LS : Account créé

  LS -> CR : create(Contact from lead)
  CR -> DB : INSERT INTO contacts
  DB --> CR : contact_id
  CR --> LS : Contact créé

  LS -> DR : create(Deal from lead)
  DR -> DB : INSERT INTO deals
  DB --> DR : deal_id
  DR --> LS : Deal créé

  LS -> DB : UPDATE lead SET status='converted',\nconverted_account_id, converted_contact_id, converted_deal_id
  DB --> LS : OK
end

LS --> API : {account, contact, deal}
API --> UI : 200 OK
UI --> U : Affichage confirmation
@enduml
```

### 3.4.3 — Cycle de vie d'un Ticket

```plantuml
@startuml Seq_Ticket
skinparam shadowing false
actor Client as C
actor "Agent Support" as S
participant "Portail / CRM" as UI
participant "API Tickets\n/api/v1/tickets" as API
participant "TicketService" as SVC
participant "EmailService" as EMAIL
database "MySQL" as DB

== Création ==
C -> UI : Créer un ticket (sujet, description, priorité)
UI -> API : POST /client/tickets
API -> SVC : create(ticket_data, user)
SVC -> DB : INSERT INTO tickets
DB --> SVC : ticket_id
SVC --> API : Ticket créé
API --> UI : 201 Created

== Assignation ==
S -> UI : Assigner le ticket à un agent
UI -> API : PATCH /tickets/{id} {assigned_to}
API -> SVC : update(ticket_id, assigned_to)
SVC -> DB : UPDATE tickets SET assigned_to = ?
DB --> SVC : OK
SVC --> API : Ticket mis à jour

== Réponse publique ==
S -> UI : Répondre au ticket
UI -> API : POST /tickets/{id}/messages {message, is_internal=false}
API -> SVC : add_message(ticket_id, message)
SVC -> DB : INSERT INTO ticket_messages
DB --> SVC : OK
SVC -> EMAIL : send_notification(client_email, ticket_ref)
EMAIL --> SVC : OK
SVC --> API : Message ajouté

== Note interne ==
S -> UI : Ajouter une note interne
UI -> API : POST /tickets/{id}/messages {message, is_internal=true}
API -> SVC : add_message(ticket_id, message)
SVC -> DB : INSERT INTO ticket_messages (is_internal=true)
DB --> SVC : OK
note right: Note visible uniquement\npar les agents internes

== Résolution ==
S -> UI : Marquer comme résolu
UI -> API : PATCH /tickets/{id} {status: "resolved"}
API -> SVC : update_status(ticket_id, resolved)
SVC -> DB : UPDATE tickets SET status='resolved', resolved_at=NOW()
DB --> SVC : OK
SVC --> API : Ticket résolu
API --> UI : 200 OK
@enduml
```

### 3.4.4 — Chatbot documentaire (RAG)

```plantuml
@startuml Seq_RAG
skinparam shadowing false
actor "Utilisateur\nauthentifié" as U
participant "Interface\n(Web / Mobile)" as UI
participant "API Chatbot\n/api/v1/chatbot" as API
participant "Chaîne RAG\n(rag_chain)" as RAG
database "ChromaDB\n(base vectorielle)" as VDB
participant "LLM Externe\n(Groq — optionnel)" as LLM

U -> UI : Poser une question
UI -> API : POST /chatbot {question}
API -> RAG : query(question)

RAG -> VDB : similarity_search(question, k=5)
VDB --> RAG : top_k documents pertinents

alt LLM disponible
  RAG -> LLM : prompt(context + question)
  LLM --> RAG : Réponse générée
else LLM indisponible (mode dégradé)
  RAG -> RAG : Construire réponse à partir\ndes extraits documentaires
end

RAG --> API : {answer, sources[]}
API --> UI : 200 OK {answer, sources}
UI --> U : Afficher la réponse\net les sources utilisées
@enduml
```

---

## Chapitre 3 — Architecture du module RAG

### 3.6.4 — Architecture RAG

```plantuml
@startuml Arch_RAG
skinparam shadowing false
skinparam rectangleRoundCorner 15
skinparam componentStyle rectangle

package "Préparation" {
  [Documents\nMarkdown] as DOCS
  [Découpage en\nfragments] as SPLIT
}

package "Indexation" {
  [Embedding\nModel] as EMB
  database "ChromaDB\n(base vectorielle)" as VDB
}

package "Requête" {
  [Question\nutilisateur] as Q
  [Recherche\ncontextuelle] as SEARCH
  [Réponse\ncontextualisée] as RESP
}

cloud "LLM Externe\n(Groq — optionnel)" as LLM

DOCS --> SPLIT : chunks
SPLIT --> EMB : texte
EMB --> VDB : vecteurs

Q --> SEARCH
SEARCH --> VDB : similarity_search
VDB --> SEARCH : top_k résultats
SEARCH --> RESP : contexte
RESP ..> LLM : prompt (si disponible)
LLM ..> RESP : génération

note bottom of RESP
  Mode dégradé : si le LLM
  n'est pas disponible, la
  réponse est construite à
  partir des extraits bruts.
end note
@enduml
```

---

## Chapitre 1 — Architecture globale

### 1.7 — Architecture globale du système CRM

```plantuml
@startuml Arch_Global
skinparam shadowing false
skinparam rectangleRoundCorner 10

actor "Utilisateur\nWeb" as UW
actor "Client\nMobile" as UM

node "Docker Compose" {

  rectangle "Frontend\nNginx + React SPA\n:3000" as FE {
    [CRM Interne]
    [Portail Client]
  }

  rectangle "Backend\nFastAPI\n:8000" as BE {
    [API REST\n/api/v1/*]
    [Module RAG\n(Chatbot)]
    [Service Email\n(SMTP)]
  }

  database "MySQL 8.0\n:3307" as DB

  database "ChromaDB\n(vectorielle locale)" as VDB
}

cloud "LLM Externe\n(Groq — optionnel)" as LLM
cloud "Serveur SMTP" as SMTP

UW --> FE : HTTPS
UM --> BE : HTTPS (API)
FE --> BE : reverse proxy /api
BE --> DB : SQLAlchemy ORM
BE --> VDB : similarity search
BE ..> LLM : appel optionnel
BE ..> SMTP : notifications email
@enduml
```
