# 🚀 Django Signals Demo

A Django project built for the **AccuKnox Trainee Assignment** that demonstrates the behavior of Django signals and implements a custom iterable `Rectangle` class.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [Demonstrations](#demonstrations)
  - [1. Django Signals Are Synchronous](#1-django-signals-are-synchronous)
  - [2. Django Signals Run in the Same Thread](#2-django-signals-run-in-the-same-thread)
  - [3. Django Signals Run in the Same Transaction](#3-django-signals-run-in-the-same-transaction)
  - [4. Custom Rectangle Class](#4-custom-rectangle-class)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)

---

## Overview

This project answers three core questions about Django signals:

| Question | Answer |
|----------|--------|
| Are Django signals synchronous? | ✅ **Yes** — the caller waits for the handler to finish |
| Do signals run in the same thread? | ✅ **Yes** — same Thread ID & Name as the caller |
| Do signals run in the same DB transaction? | ✅ **Yes** — rolled back together with the caller |

It also implements a custom `Rectangle` class with `__iter__` support as a standalone Python exercise.

---

## Project Structure

```
AccuKnox/
├── assignment_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── signals_demo/                # Main Django app
│   ├── migrations/
│   ├── templates/
│   │   └── signals_demo/
│   │       └── dashboard.html   # Interactive web UI
│   ├── management/
│   │   └── commands/
│   │       └── run_signals_demo.py  # CLI demo runner
│   ├── models.py                # DemoModel
│   ├── signals.py               # Custom signals & receivers
│   ├── views.py                 # API views for each demo
│   ├── urls.py
│   └── utils.py                 # Rectangle class
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## Features

- 🎯 **Interactive Web Dashboard** — Run each demo with a single button click and see live logs
- 🔌 **3 Signal Demonstrations** — Synchronicity, threading, and transaction behavior
- 📐 **Custom Rectangle Class** — Iterable class yielding `length` and `width` as dicts
- 🖥️ **CLI Management Command** — Run all demos from the terminal

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/SHasHwatModi05/django-signals-demo.git
cd django-signals-demo

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate
```

---

## Running the Project

```bash
# Start the development server
python manage.py runserver
```

Then open your browser at: **http://127.0.0.1:8000/**

You'll see the interactive dashboard with buttons for each demonstration.

### Run via CLI (Management Command)

```bash
python manage.py run_signals_demo
```

---

## Demonstrations

### 1. Django Signals Are Synchronous

**Question:** Are Django signals executed synchronously by default?

**How it works:**
- The caller sends `sync_async_signal`
- The receiver simulates a heavy task using `time.sleep(2)`
- The caller's "Returned to caller" message only prints **after** the receiver finishes

**Proof:** The total elapsed time is always ≥ 2 seconds — the caller was blocked.

```python
@receiver(sync_async_signal)
def handle_sync_async(sender, **kwargs):
    time.sleep(2)  # Blocks the caller — proves synchronous execution
```

**Answer:** ✅ **Yes, Django signals are synchronous by default.**

---

### 2. Django Signals Run in the Same Thread

**Question:** Do Django signals run in the same thread as the caller?

**How it works:**
- The caller captures its Thread ID and Thread Name
- The receiver also captures its Thread ID and Thread Name
- Both values are compared

**Proof:** The Thread ID is **identical** in both the caller and the receiver.

```python
@receiver(thread_check_signal)
def handle_thread_check(sender, **kwargs):
    thread_id = threading.get_ident()
    thread_name = threading.current_thread().name
    # Same as the caller's thread
```

**Answer:** ✅ **Yes, Django signals run in the same thread as the caller.**

---

### 3. Django Signals Run in the Same Transaction

**Question:** Do Django signals run in the same database transaction as the caller?

**How it works:**
1. A `transaction.atomic()` block is opened
2. Caller creates a DB record ("Caller Record")
3. Signal is sent — receiver can **see** the caller's record and creates its own ("Record created by Receiver")
4. A `ValueError` is raised to **force a rollback**
5. **Both** records disappear — final DB count = 0

**Proof:** The receiver's record is rolled back along with the caller's, confirming they share the same transaction.

```python
with transaction.atomic():
    DemoModel.objects.create(name="Caller Record")
    transaction_check_signal.send(sender=None)
    raise ValueError("Simulated Rollback")  # Rolls back both records
```

**Answer:** ✅ **Yes, Django signals execute within the same database transaction as the caller.**

---

### 4. Custom Rectangle Class

**Question:** Create a `Rectangle` class that is iterable, yielding `length` and `width` as dictionaries.

**Implementation (`signals_demo/utils.py`):**

```python
class Rectangle:
    def __init__(self, length: int, width: int):
        if not isinstance(length, int) or not isinstance(width, int):
            raise TypeError("length and width must be integers")
        self.length = length
        self.width = width

    def __iter__(self):
        yield {'length': self.length}
        yield {'width': self.width}
```

**Usage:**

```python
rect = Rectangle(10, 5)
for item in rect:
    print(item)

# Output:
# {'length': 10}
# {'width': 5}
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Interactive dashboard |
| `POST` | `/test-sync-async/` | Run synchronicity demo |
| `POST` | `/test-thread-check/` | Run thread check demo |
| `POST` | `/test-transaction-check/` | Run transaction demo |
| `POST` | `/test-rectangle/` | Run Rectangle iteration demo |

---

## Tech Stack

| Technology | Version |
|------------|---------|
| Python | 3.10+ |
| Django | ≥ 4.2, < 5.1 |
| SQLite | (default Django DB) |

---

## Author

**Shashwat Modi**
Trainee Assignment — AccuKnox
