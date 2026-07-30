# DiviBank
Python banking application with NUBAN generation, phone validation, and transaction management

# DiviBank 🏦

A console-based banking application built in Python, simulating core Nigerian banking operations — account creation, secure login, and a customer dashboard — with real-world validation logic modeled on actual Nigerian banking standards.

## About This Project

DiviBank is a self-directed learning project built entirely on an Android phone using Pydroid 3, as part of my journey teaching myself software development alongside my Computer Science degree at the University of Benin. It's my way of applying what I'm learning — exception handling, data validation, hashing, file I/O, and SQLite — to something that mirrors real fintech systems used in Nigeria.

## What It Does

- **Account Registration** — collects personal details, validates them, and generates a unique account number using the actual CBN (Central Bank of Nigeria) weighted check-digit algorithm used for NUBAN numbers
- **Phone Number Validation** — detects the network provider (MTN, Airtel, Glo, 9mobile) from a Nigerian phone number using real prefix mappings
- **Secure Authentication** — passwords and transaction PINs are hashed (SHA-256) before storage, with input rules enforced (length, character variety, no sequential/repeated PINs)
- **Account Lockout** — temporarily locks an account after repeated failed login attempts, with automatic unlock after a cooldown period
- **BVN & Email Validation** — enforces correct formats for Bank Verification Number and email input
- **Dashboard** — displays balance and account details, with a menu for banking actions
- **Persistent Storage** — account data is saved via SQLite (`bank.db`) and a backup flat file, with custom exceptions used throughout for clean error handling

## Current Status

This is a work in progress. Registration, login, validation, and the dashboard shell are functional. Features like Transfer, Withdraw, Bills, Airtime, Data purchase, and Transaction History are stubbed out in the dashboard menu and are the next things I'm building.

## Files

- `bank_helpers.py` — all core logic: validation functions, custom exceptions, database setup, registration, login, and dashboard
- `main.py` — entry point that runs the login/registration flow and launches the dashboard

## Why This Project

I wanted to go beyond tutorials and build something that solves a real, local problem — a banking system that reflects how Nigerian fintech actually works, from NUBAN generation to network-based phone validation. It's been a hands-on way to practice exception handling, security fundamentals, and structuring a growing codebase.
