import pandas as pd
import random
from datetime import datetime, timedelta

class EgyptianTelecomDataCollector:
    def __init__(self):
        self.operators = {
            'vodafone': {'color': '#E60000', 'market_share': 0.40},
            'orange': {'color': '#FF6600', 'market_share': 0.35},
            'etisalat': {'color': '#00A1E9', 'market_share': 0.15},
            'we': {'color': '#800080', 'market_share': 0.10}
        }
        
        self.egyptian_governorates = [
            'Cairo', 'Giza', 'Alexandria', 'Qalyubia', 'Port Said', 'Suez',
            'Dakahlia', 'Sharqia', 'Monufia', 'Gharbia', 'Beheira', 'Ismailia',
            'Faiyum', 'Beni Suef', 'Minya', 'Asyut', 'Sohag', 'Qena', 'Luxor', 'Aswan'
        ]
    
    def generate_realistic_complaints(self, num_complaints=500):
        """Generate realistic Egyptian telecom complaints"""
        
        # Complaint templates in Arabic and English (mixed as in real Egyptian social media)
        complaint_templates = [
            # Internet issues
            {"category": "internet", "texts": [
                "الإنترنت بطيء جداً في {location} منذ ٣ أيام",
                "Slow internet in {location}, can't even browse",
                "مشكلة في النت في منطقة {location}",
                "Internet keeps disconnecting in {location}",
                "سرعة النت سيئة اليوم في {location}"
            ]},
            # Network issues
            {"category": "network", "texts": [
                "الإشارة ضعيفة في {location}",
                "No network coverage in {location} area",
                "مشكلة في الشبكة في {location}",
                "Network keeps dropping in {location}",
                "لا يوجد إشارة في الطابق السفلي في {location}"
            ]},
            # Billing issues
            {"category": "billing", "texts": [
                "الفاتورة غير صحيحة هذا الشهر",
                "Incorrect charges on my bill",
                "خصم مبلغ غير صحيح من رصيدي",
                "Bill amount is wrong this month",
                "فاتورتي أعلى من المعتاد بدون سبب"
            ]},
            # Balance issues
            {"category": "balance", "texts": [
                "الرصيد ينتهي بسرعة كبيرة",
                "My balance finishes too fast",
                "مشكلة في شحن الرصيد",
                "Balance deduction is too quick",
                "رصيدي انتهى فجأة"
            ]},
            # Customer service
            {"category": "customer_service", "texts": [
                "خدمة العملاء لا ترد على الاتصالات",
                "Customer service not answering",
                "لا يوجد رد من خدمة العملاء",
                "Waiting 30 minutes for customer service",
                "خدمة العملاء سيئة جداً"
            ]},
            # Calls issues
            {"category": "calls", "texts": [
                "المكالمات تنقطع فجأة",
                "Calls dropping frequently",
                "مشكلة في إجراء المكالمات",
                "Can't make calls, network busy",
                "جودة المكالمات سيئة"
            ]}
        ]
        
        complaints_data = []
        
        for i in range(num_complaints):
            # Select operator based on market share
            operator = random.choices(
                list(self.operators.keys()),
                weights=[op['market_share'] for op in self.operators.values()]
            )[0]
            
            # Select complaint category
            category_data = random.choice(complaint_templates)
            category = category_data['category']
            
            # Select location (some complaints might not have location)
            location = random.choice(self.egyptian_governorates) if random.random() > 0.3 else "Unknown"
            
            # Select complaint text
            complaint_template = random.choice(category_data['texts'])
            complaint_text = complaint_template.format(location=location)
            
            # Generate realistic dates (last 60 days)
            complaint_date = datetime.now() - timedelta(days=random.randint(0, 60))
            
            # Generate realistic sentiment (mostly negative for complaints)
            sentiment_score = random.uniform(-0.8, 0.2)
            
            # Generate engagement metrics
            likes = random.randint(0, 15)
            replies = random.randint(0, 5)
            
            complaints_data.append({
                'complaint_id': i + 1,
                'operator': operator,
                'complaint_text': complaint_text,
                'complaint_category': category,
                'sentiment_score': round(sentiment_score, 3),
                'date': complaint_date.date(),
                'governorate': location,
                'likes': likes,
                'replies': replies,
                'source': 'synthetic',
                'collection_timestamp': datetime.now()
            })
        
        return pd.DataFrame(complaints_data)
    
    def save_complaints_data(self, df, filename='egypt_telecom_complaints.csv'):
        """Save complaints data to CSV"""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Saved {len(df)} complaints to {filename}")

# Generate and save data
if __name__ == "__main__":
    collector = EgyptianTelecomDataCollector()
    complaints_df = collector.generate_realistic_complaints(600)
    collector.save_complaints_data(complaints_df)
    print("Sample of generated data:")
    print(complaints_df[['operator', 'complaint_category', 'complaint_text', 'sentiment_score']].head(10))