# 📱 Africa's Talking Integration

## Overview

Complete integration with Africa's Talking API for SMS, Voice, USSD, and Airtime services - perfect for the Marketing and Growth Solutions Hackathon!

## ✅ Implemented Features

### 1. **SMS Services**
- ✅ Send SMS to multiple recipients
- ✅ Lead notification SMS
- ✅ Lead details SMS
- ✅ Automatic phone number formatting
- ✅ Cost tracking

### 2. **Voice Services**
- ✅ Initiate voice calls
- ✅ Text-to-speech integration
- ✅ Lead verification calls
- ✅ Automated follow-ups

### 3. **Airtime Services**
- ✅ Send airtime rewards
- ✅ Multi-currency support (KES, UGX, TZS, etc.)
- ✅ Incentive system for referrals

### 4. **USSD Support**
- ✅ USSD menu framework (requires callback URL setup)

## 🚀 API Endpoints

### Send SMS
```
POST /api/v1/sms/send
```

**Request:**
```json
{
  "phone_numbers": ["+254712345678", "+254798765432"],
  "message": "Your leads are ready! Check your dashboard.",
  "sender_id": "LEADGEN"  // Optional
}
```

### Send Lead Notification
```
POST /api/v1/sms/send-lead-notification
```

**Request:**
```json
{
  "phone": "+254712345678",
  "lead_summary": {
    "total": 10,
    "premium": 3,
    "high": 5,
    "dashboard_url": "https://your-dashboard.com"
  }
}
```

### Initiate Voice Call
```
POST /api/v1/voice/call
```

**Request:**
```json
{
  "phone_number": "+254712345678",
  "message": "Hello, we have generated leads for you. Would you like to hear more?"
}
```

### Send Airtime
```
POST /api/v1/airtime/send
```

**Request:**
```json
{
  "phone_number": "+254712345678",
  "amount": "100",
  "currency": "KES"
}
```

## 🔧 Setup

### 1. Get Africa's Talking Credentials

1. Sign up at: https://account.africastalking.com
2. Create an application
3. Get your:
   - **Username**
   - **API Key**

### 2. Add to `.env`

```bash
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
AFRICASTALKING_SANDBOX=true  # Use sandbox for testing
```

### 3. Restart Backend

```bash
# Stop current server (Ctrl+C)
# Restart
python api.py
```

## 📱 Use Cases for Hackathon

### 1. **SMS Lead Notifications**
When leads are generated, automatically send SMS:
```python
# In your lead generation flow
at_service = get_africastalking_service()
if at_service:
    at_service.send_lead_notification_sms(
        phone="+254712345678",
        lead_summary={
            "total": 10,
            "premium": 3,
            "high": 5
        }
    )
```

### 2. **Voice Lead Verification**
Call leads to verify contact information:
```python
at_service.initiate_voice_call(
    phone_number="+254712345678",
    message="Hello, this is LeadGen AI. We'd like to verify your contact information."
)
```

### 3. **Airtime Rewards**
Reward users for successful conversions:
```python
at_service.send_airtime(
    phone_number="+254712345678",
    amount="100",
    currency="KES"
)
```

### 4. **USSD Lead Requests**
Allow users to request leads via USSD:
```
*384*123# → Request leads
*384*123*1# → Request technology leads
*384*123*2# → Request healthcare leads
```

## 🎯 Hackathon Integration Ideas

### **Idea 1: SMS + Voice Combo**
1. Generate leads
2. Send SMS with summary
3. Follow up with voice call for premium leads

### **Idea 2: Airtime Incentives**
1. User generates leads
2. For every 5 premium leads, reward with airtime
3. Track conversions and reward success

### **Idea 3: USSD Lead Requests**
1. SME dials `*384*123#`
2. Selects industry via USSD menu
3. Receives leads via SMS
4. Can request voice summary

### **Idea 4: Multi-Channel Outreach**
1. Email lead (existing)
2. SMS lead (Africa's Talking)
3. Voice call (Africa's Talking)
4. Track which channel works best

## 📊 Phone Number Format

### Supported Formats:
- **International**: `+254712345678` ✅ (Recommended)
- **Local**: `0712345678` ✅ (Auto-converted)
- **With spaces**: `+254 712 345 678` ✅ (Auto-formatted)

### Country Codes:
- Kenya: `+254`
- Nigeria: `+234`
- South Africa: `+27`
- Ghana: `+233`
- Uganda: `+256`
- Tanzania: `+255`

## 🔒 Security

- API keys stored in environment variables
- Sandbox mode for testing
- Production mode for live deployment
- Phone number validation
- Rate limiting (handled by Africa's Talking)

## 💰 Pricing

### Sandbox (Free):
- Unlimited SMS (test numbers only)
- Limited voice calls
- Test airtime

### Production:
- SMS: ~KES 1-2 per SMS
- Voice: ~KES 5-10 per minute
- Airtime: Face value + small fee

## 🐛 Troubleshooting

### "Africa's Talking not configured"
- ✅ Check `.env` file has credentials
- ✅ Verify `AFRICASTALKING_USERNAME` and `AFRICASTALKING_API_KEY`
- ✅ Restart backend after adding credentials

### "SMS not sending"
- ✅ Check phone number format (include country code)
- ✅ Verify sandbox mode (test numbers only in sandbox)
- ✅ Check API key is valid
- ✅ Review Africa's Talking dashboard for errors

### "Voice call failed"
- ✅ Verify phone number format
- ✅ Check caller ID is approved
- ✅ Ensure sufficient credits

## 📚 Documentation

- **Africa's Talking Docs**: https://developers.africastalking.com
- **SMS API**: https://developers.africastalking.com/docs/sms/overview
- **Voice API**: https://developers.africastalking.com/docs/voice/overview
- **Airtime API**: https://developers.africastalking.com/docs/airtime/overview

## 🎉 Ready for Hackathon!

Your application now has:
- ✅ SMS notifications
- ✅ Voice calls
- ✅ Airtime rewards
- ✅ Multi-channel outreach
- ✅ African market focus

**Perfect for the Marketing and Growth Solutions Hackathon!** 🚀

