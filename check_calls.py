import os
from sqlalchemy import create_all, text
from database import SessionLocal
from models import AdvisoryCall
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

def check():
    db = SessionLocal()
    calls = db.query(AdvisoryCall).order_by(AdvisoryCall.id.desc()).limit(5).all()
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    print(f"{'ID':<5} | {'SID':<34} | {'Status':<10} | {'Duration':<8}")
    print("-" * 70)
    for c in calls:
        print(f"{c.id:<5} | {c.twilio_sid:<34} | {c.call_status:<10} | {c.call_duration:<8}")
        
        if c.twilio_sid:
            try:
                t_call = client.calls(c.twilio_sid).fetch()
                print(f"  Twilio actual: Status={t_call.status}, Duration={t_call.duration}, DateCreated={t_call.date_created}")
                
                notifs = client.api.accounts(TWILIO_ACCOUNT_SID).calls(c.twilio_sid).notifications.list(limit=3)
                for n in notifs:
                    print(f"    ERR: {n.error_code} - {n.message_text[:100]}")
            except Exception as e:
                print(f"    Failed to fetch Twilio info: {e}")
    db.close()

if __name__ == "__main__":
    check()
