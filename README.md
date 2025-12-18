# Transaction Webhook Service

## 🌐 Live API
Base URL: https://transaction-webhook.up.railway.app/

## 🛠️ Tech Stack
* FastAPI — HTTP API framework
* PostgreSQL — persistent storage for transactions
* Redis + RQ — background job queue and worker
* Docker — containerization
* Railway — cloud deployment (API + worker + databases)

## API Endpoints
### Health Check

GET - "/"
##### Response
    {
        "status": "HEALTHY",
        "current_time": "2024-01-15T10:30:00Z"
    }

### Receive Transaction Webhook

POST - "/v1/webhooks/transactions"
##### Request body
    {
        "transaction_id": "txn_abc123def456",
        "source_account": "acc_user_789",
        "destination_account": "acc_merchant_456",
        "amount": 1500,
        "currency": "INR"
    }
##### Response
    {
        "message": "accepted"
    }

## Project Setup
### Pre-requisites
* Python 3.11+
* PostgreSQL
* Redis

### Environment Variables
#### Create a .env file
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/transactions
    REDIS_URL=redis://localhost:6379

#### Install dependencies
    pip install -r requirements.txt

## Start the services
Have two terminals open

    # Terminal 1: API
    uvicorn app.main:app --reload

    #Terminal 2: Worker
    rq worker transactions

## Testing the Service
### Single Transaction
    curl -X POST http://localhost:8000/v1/webhooks/transactions \
    -H "Content-Type: application/json" \
    -d '{
        "transaction_id": "txn_test_001",
        "source_account": "acc_user_001",
        "destination_account": "acc_merchant_001",
        "amount": 1500,
        "currency": "INR"
    }'

Validation: 202 Accepted within 500ms

### Within 30 seconds
    curl http://localhost:8000/v1/transactions/txn_test_001

Validation: Status is still PROCESSING

### After ~30 seconds
    curl http://localhost:8000/v1/transactions/txn_test_001

Validation: Status becomes PROCESSED

### Duplicate Prevention (Idempotency)
    for i in {1..5}; do
    curl -X POST http://localhost:8000/v1/webhooks/transactions \
    -H "Content-Type: application/json" \
    -d '{
        "transaction_id": "txn_dupe_001",
        "source_account": "acc_user_001",
        "destination_account": "acc_merchant_001",
        "amount": 1500,
        "currency": "INR"
        }'
    done

Validation: Only one transaction is processed and stored

### Performance Under Load
    for i in {1..10}; do
    curl -o /dev/null -s -X POST http://localhost:8000/v1/webhooks/transactions \
    -H "Content-Type: application/json" \
    -d "{
        \"transaction_id\": \"txn_load_$i\",
        \"source_account\": \"acc_user_001\",
        \"destination_account\": \"acc_merchant_001\",
        \"amount\": 1000,
        \"currency\": \"INR\"
        }" &
    done
    wait

Validation: All requests return immediately while processing happens asynchronously

## Technical Design Choices
#### Asynchronous Processing
* Webhook endpoint only persists data and enqueues a job
* Actual processing runs in a separate background worker
* Ensures fast responses regardless of processing time

#### Redis + RQ
* Redis is used as a message broker
* RQ worker ensures background jobs are execute independently of HTTP requests
* Worker survives API restarts

#### Idempotency
* transaction_id is enforced as a primary key
* Duplicate webhooks are safely ignored without errors or reprocess

#### Deployment Choice
* Railway is used to run the API and worker as two separate services
* Allowing realistic production-style background process
* Manages Postgres and Redis reducing operational complexity

```
Note: Request latency may vary due to cloud cold starts and network RTT (Round Trip Time). The webhook handler itself is non-blocking and independent of processing time.
```