# Online-blood-donation-management-system

**Project Overview

The Online Blood Donation Management System (OBDMS) eliminates fake blood inventory concepts and ensures that blood donation happens only when a valid request exists.

It follows a donor-first, request-based architecture where:

Donors cannot donate without a real request

Matching is based on medical blood compatibility

Contact details are shared only after acceptance

No fake stock or blood bank inventory logic

**Key Features

Request-based blood donation system

Medical blood compatibility matching

Secure donor privacy

Role-based access (Donor / Hospital / Requester)

Email notifications (SMTP integration)

Donation history tracking

No inventory or fake stock logic

**Core Modules

Donor Module

Hospital Module

Blood Request Module

Matching & Notification Module

Donation Tracking Module

(Admin Module – Future Enhancement)

**System Flow

User or Hospital creates a blood request

System matches compatible donors by blood group & city

Donors receive email notification

Donor accepts or rejects request

Contact details shared after acceptance

Physical donation occurs

Request marked as fulfilled

**Technology Stack
Frontend

HTML

CSS

Bootstrap

Backend

Python

Django Framework

Database

SQLite3

Email & Notifications

Gmail SMTP

In-app notification system

🗄 Database Models Used

User (Django built-in)

Donor

Hospital

BloodRequest

RequestMatch

DonorDonation

DonorNotification

**Security & Validation

Role-based authentication

Donor cannot donate without accepted request

Request cannot be modified after fulfillment/cancellation

Self-donation prevention

Aadhaar stored as last 4 digits only

Full model-level validation using clean()

**Installation Guide
1️⃣ Clone Repository
git clone https://github.com/YOUR-USERNAME/Online-blood-donation-management-system.git
cd Online-blood-donation-management-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Run Migrations
python manage.py migrate

5️⃣ Run Server
python manage.py runserver

📄 requirements.txt
Django>=5.0

🔮 Future Enhancements

SMS alerts for emergencies

Distance-based donor matching

AI-based blood demand prediction

Analytics dashboard for hospitals

Mobile application integration

Admin monitoring module

📚 References

Django Official Documentation

Python Official Documentation
