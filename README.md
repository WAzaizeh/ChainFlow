# chainflow

> Small business operations platform: task tracking with reviews, inventory management, and franchise supply ordering system.

## Features

### 🎯 Task Management
- Employee task tracking with history
- Performance reviews and feedback
- Task assignment and deadline monitoring

### 📦 Inventory Control
- Unit conversion system
- Stock level tracking
- Low inventory alerts
- Change history and audit trail

### 🏪 Franchise Operations
- Centralized supply ordering
- HQ-franchise communication
- Order tracking and fulfillment

## Tech Stack

- **Backend & Frontend **: FastHTML
- **Database**: Appwrite and PostgreSQL
- **Authentication**: Appwrite Auth

## Development

### Prerequisites

- Python 3.9+
- Appwrite instance

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chainflow.git
cd chainflow
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Appwrite credentials
```

4. Run development server:
```bash
uvicorn app.main:app --reload --port 5000
```

## Project Structure

```
chainflow/
── app/
│   ├── layout/      # UI components
│   ├── models/      # Data models
│   ├── routes/      # API endpoints
│   └── db/          # Database operations
├── terraform/       # Infrastructure as Code
│   ├── main.tf     # Main Terraform configuration
│   ├── variables.tf # Variable definitions
│   └── outputs.tf  # Output definitions
├── requirements.txt # Project dependencies
└── Procfile         # serverless deployment configuration
```

## Infrastructure Setup (Terraform)

1. Initialize Terraform:
```bash
cd terraform
terraform init
```

2. Plan deployment:
```bash
terraform plan -var-file="dev.tfvars"
```

3. Apply changes:
```bash
terraform apply -var-file="dev.tfvars"
```

## Environment Variables
Required variables in `dev.tfvars`:
- `project_id`: GCP project ID
- `region`: GCP region
- `service_name`: Cloud Run service name
- `image_name`: Container image name
```