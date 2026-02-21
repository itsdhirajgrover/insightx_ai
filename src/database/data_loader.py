import random
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.database import SessionLocal, init_db
from src.database.models import Transaction
import os

class DataLoader:
    """Load and manage transaction data"""
    
    def __init__(self):
        self.categories = [
            "Food", "Entertainment", "Travel", "Shopping", "Utilities", 
            "Healthcare", "Education", "Bills", "Downloads", "Other"
        ]
        self.states = [
            "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana",
            "Gujarat", "Rajasthan", "Punjab", "West Bengal", "Uttar Pradesh",
            "Andhra Pradesh", "Haryana", "Madhya Pradesh", "Bihar", "Odisha"
        ]
        self.devices = ["iOS", "Android", "Web"]
        self.networks = ["WiFi", "4G", "5G"]
        self.age_groups = ["13-18", "18-25", "25-35", "35-45", "45-55", "55+"]
        self.statuses = ["success", "failed", "pending"]
    
    def generate_synthetic_data(self, num_records: int = 250000) -> list:
        """Generate synthetic transaction data"""
        print(f"Generating {num_records} synthetic transactions...")
        
        transactions = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_records):
            # Varied amounts by category
            category = random.choice(self.categories)
            base_amount = {
                "Food": 500, "Entertainment": 2000, "Travel": 5000,
                "Shopping": 3000, "Utilities": 1500, "Healthcare": 4000,
                "Education": 8000, "Bills": 2000, "Downloads": 500, "Other": 2000
            }.get(category, 2000)
            
            amount = base_amount + random.gauss(0, base_amount * 0.3)
            amount = max(100, min(50000, amount))  # Clamp between 100 and 50000
            
            # Higher fraud rate in certain categories
            fraud_chance = {
                "Shopping": 0.08, "Downloads": 0.06, "Entertainment": 0.04,
                "Travel": 0.03, "Other": 0.05
            }.get(category, 0.02)
            
            # Higher failure rate on poor networks
            device = random.choice(self.devices)
            network = random.choice(self.networks)
            failure_chance = {
                "5G": 0.01, "WiFi": 0.02, "4G": 0.03
            }.get(network, 0.02)
            
            status = "failed" if random.random() < failure_chance else random.choice(["success", "pending"]) if random.random() < 0.05 else "success"
            
            transaction = Transaction(
                user_id=random.randint(1, 50000),
                amount=round(amount, 2),
                category=category,
                timestamp=base_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                ),
                device_type=device,
                network_type=network,
                state=random.choice(self.states),
                age_group=random.choice(self.age_groups),
                status=status,
                fraud_flag=random.random() < fraud_chance,
                merchant_id=random.randint(1000, 9999),
                latitude=random.uniform(8.0, 35.0),
                longitude=random.uniform(68.0, 97.0)
            )
            transactions.append(transaction)
            
            if (i + 1) % 50000 == 0:
                print(f"  Generated {i + 1}/{num_records} transactions")
        
        return transactions
    
    def load_from_csv(self, csv_path: str) -> list:
        """Load transactions from CSV file"""
        print(f"Loading data from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        transactions = []
        
        print(f"CSV columns: {df.columns.tolist()}")
        print(f"Total records in CSV: {len(df)}")
        
        for idx, row in df.iterrows():
            # Map CSV columns to Transaction model
            # Handle different column naming conventions
            user_id = int(row.get('user_id', row.get('sender_id', idx % 50000)))
            amount = float(row.get('amount (INR)', row.get('amount', 0)))
            category = str(row.get('merchant_category', row.get('category', 'Other')))
            timestamp = pd.to_datetime(row.get('timestamp', pd.Timestamp.now()))
            device_type = str(row.get('device_type', 'Web'))
            network_type = str(row.get('network_type', 'WiFi'))
            state = str(row.get('sender_state', row.get('state', 'Delhi')))
            age_group = str(row.get('sender_age_group', row.get('age_group', '25-35')))
            status = str(row.get('transaction_status', row.get('status', 'success')))
            fraud_flag = bool(row.get('fraud_flag', False))
            merchant_id = int(row.get('merchant_id', idx % 10000))
            
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                category=category,
                timestamp=timestamp,
                device_type=device_type,
                network_type=network_type,
                state=state,
                age_group=age_group,
                status=status,
                fraud_flag=fraud_flag,
                merchant_id=merchant_id,
                latitude=float(row.get('latitude', 0)),
                longitude=float(row.get('longitude', 0))
            )
            transactions.append(transaction)
            
            if (idx + 1) % 50000 == 0:
                print(f"  Processed {idx + 1}/{len(df)} records")
        
        print(f"Loaded {len(transactions)} transactions from CSV")
        return transactions
    
    def insert_to_database(self, transactions: list, db: Session = None):
        """Insert transactions into database"""
        if db is None:
            db = SessionLocal()
        
        print(f"Inserting {len(transactions)} transactions into database...")
        
        # Batch insert for performance
        batch_size = 5000
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i+batch_size]
            db.add_all(batch)
            db.commit()
            print(f"  Committed {min(i+batch_size, len(transactions))}/{len(transactions)} transactions")
        
        db.close()
        print("✓ Data import complete!")
    
    def load_and_populate(self, csv_path: str = None, num_synthetic: int = 250000):
        """Load data (from CSV or generate synthetic) and populate database"""
        
        # Initialize database
        init_db()
        db = SessionLocal()
        
        # Check if database already has data
        existing_count = db.query(Transaction).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} transactions. Skipping population.")
            db.close()
            return
        
        # Load data
        if csv_path and os.path.exists(csv_path):
            transactions = self.load_from_csv(csv_path)
        else:
            transactions = self.generate_synthetic_data(num_synthetic)
        
        # Insert into database
        self.insert_to_database(transactions, db)

if __name__ == "__main__":
    import sys
    
    loader = DataLoader()
    
    # Check for CSV file argument
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    if csv_file:
        loader.load_and_populate(csv_path=csv_file)
    else:
        print("No CSV file provided. Generating synthetic data...")
        loader.load_and_populate()
