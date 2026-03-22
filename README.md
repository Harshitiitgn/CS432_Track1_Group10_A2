# CS432_Track1_Group10_A2

**CS 432 – Databases | Assignment 2 | IIT Gandhinagar**
**Instructor:** Dr. Yogesh K. Meena | Semester II (2025–2026)

**Video Link**:

Module A: https://www.youtube.com/watch?v=bfksJJLcyYY


Module B: https://www.youtube.com/watch?v=Xnf_NpJOGJw

---

## Repository Structure

```
CS432_Track1_Group10_A2/
├── Module_A/                   # Lightweight DBMS with B+ Tree Index
│   ├── database/
│   │   ├── __init__.py
│   │   ├── bplustree.py
│   │   ├── bruteforce.py
│   │   ├── table.py
│   │   ├── db_manager.py
│   │   └── performance.py
│   ├── report.ipynb
│   └── requirements.txt
│
└── Module_B/                   # Hostel Management System — API, RBAC & Optimisation
    ├── Extras/                 # this has all images and plots that were used directly or indirectly 
    ├── app/
    │   ├── src/
    │   │   ├── components/     # React UI (AdminDashboard, MemberDashboard, Login, QRScanner)
    │   │   ├── routes/         # Express API routes
    │   │   ├── middleware/     # Auth, RBAC middleware
    │   ├── sql/
    │   │   ├── seed.sql/       # Seed data (~900 rows)
    │   │   └── hostel.sql      # Schema + constraints + triggers
    │   ├── logs/
    │   │   ├── access.log       
    │   │   └── audit.log           # Runtime audit trail (API + DB-level)
    │   ├── server.js           # Express entry point
    │   └── package.json
    ├── logs/
    │   ├── access.log       
    │   └── audit.log           # Runtime audit trail (API + DB-level)
    ├── sql/
    │   ├── seed.sql       # Seed data (~900 rows)
    │   └── hostel.sql      # Schema + constraints + triggers
    ├── Module_B_Report.pdf
    └── BenchmarkComparison.ipynb
```

---

## Module A — Lightweight DBMS with B+ Tree Index

### Overview

Implements a B+ Tree indexing engine from scratch in Python, serving as the core of a lightweight in-memory DBMS. Includes a full benchmarking suite comparing the B+ Tree against a brute-force linear approach, and tree visualisation using Graphviz.

### What each file does

| File | Purpose |
|------|---------|
| `bplustree.py` | Full B+ Tree with insert, delete, search, range query, update, get_all, and Graphviz visualisation |
| `bruteforce.py` | List-based DB with O(n) operations — performance baseline |
| `table.py` | Wraps B+ Tree into a named-column Table with aggregate functions (sum, avg, min, max) |
| `db_manager.py` | Top-level manager — create/drop tables, pass-through DML |
| `performance.py` | `PerformanceAnalyzer` — timed benchmarks for insert, search, delete, range, random ops, and memory; generates Matplotlib plots |
| `report.ipynb` | Main deliverable — demos, benchmarks, visualisations, and analysis |

### Setup

```bash
cd CS432_Track1_Group10_A2/Module_A

# (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

> Graphviz also requires the system binary:
> - **Ubuntu/Debian:** `sudo apt install graphviz`
> - **macOS:** `brew install graphviz`
> - **Windows:** Download from [graphviz.org](https://graphviz.org/download/) and add to PATH

### Running the Notebook

```bash
jupyter notebook report.ipynb
```

Run all cells top to bottom via **Cell → Run All**, or `Shift + Enter` per cell. Also works in JupyterLab and VS Code with the Jupyter extension.

### Notebook Structure

| Section | Content |
|---------|---------|
| 1. Introduction | Problem statement and B+ Tree motivation |
| 2. Setup | Module imports |
| 3. Core B+ Tree Operations | Live demo of insert, search, range query, update, delete |
| 4. Table & DB Manager | CRUD and aggregations on a sample table |
| 5. Graphviz Visualisation | Internal nodes, leaf nodes, and leaf linked-list arrows |
| 6. Performance Benchmarks | `PerformanceAnalyzer` across multiple dataset sizes; 6 comparison plots |
| 7. Analysis & Discussion | Time complexity breakdown |
| 8. Conclusion | Findings, challenges, potential improvements |

### Quick Smoke Test

```bash
python3 -c "
from database import BPlusTree, BruteForceDB, DatabaseManager

tree = BPlusTree(order=4)
for i in [10, 5, 20, 3, 7, 15, 25]:
    tree.insert(i, {'id': i})

print('All keys:   ', [k for k, _ in tree.get_all()])
print('Search 15:  ', tree.search(15))
print('Range 5-15: ', [k for k, _ in tree.range_query(5, 15)])
tree.delete(7)
print('After del 7:', [k for k, _ in tree.get_all()])

db = DatabaseManager('TestDB')
t  = db.create_table('items', primary_key='id', order=4)
for i in range(1, 6):
    t.insert({'id': i, 'score': i * 10})
print('Row count:  ', t.count())
print('Avg score:  ', t.aggregate('score', 'avg'))
print('All OK.')
"
```

### Key Design Decisions

- **Order 4 B+ Tree** — each node holds at most 3 keys; chosen to show splitting clearly at small dataset sizes.
- **Copy-up vs Push-up** — on leaf splits the middle key is copied up (leaf retains it); on internal splits it is pushed up (removed from child). Standard B+ Tree semantics.
- **Leaf linked list** — every leaf holds a `next` pointer to the adjacent leaf, enabling O(log n + k) range scans.
- **Underflow handling** — deletion borrows from a sibling first; merges only when both siblings are at minimum occupancy.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: graphviz` | `pip install graphviz` |
| Graphviz renders but no image shown | Install the system binary and restart the kernel |
| `jupyter: command not found` | `pip install jupyter` or `python3 -m jupyter notebook` |
| Kernel dies on performance cell | Reduce `sizes` in the benchmark cell (e.g. `range(100, 3000, 500)`) |

---

## Module B — Hostel Management System

### Overview

A full-stack web application for hostel administration. Implements secure HttpOnly cookie-based session management, Role-Based Access Control (RBAC), dual-layer audit logging, and SQL indexing with quantitative benchmarking across 33 API endpoints.

### Key Features

**Admin**
- Unified dashboard with real-time analytics on occupancy, complaints, and visitor traffic
- Full CRUD over members, rooms, allocations, fee payments, complaints, and maintenance requests
- Interactive room map and warden directory
- Audit log tracking all POST/PUT/DELETE actions

**Member Portal**
- QR code generation for gate entry/exit
- View room assignment, check-in history, and warden contacts
- Submit maintenance requests and track status
- Log and track visitors

**Security**
- HttpOnly, SameSite cookie-based JWT — tokens inaccessible to client-side JavaScript
- `requireAdmin` middleware blocks all non-admin access to administrative endpoints
- `requireOwnershipOrAdmin` middleware prevents horizontal privilege escalation (IDOR)
- Dual-layer audit logging: Morgan to `audit.log` (API layer) + SQLite AFTER triggers to `AuditLog` table (DB layer)

### Technical Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS 4 |
| Backend | Node.js + Express |
| Database | SQLite |
| Auth | HttpOnly Cookie-based JWT (bcryptjs) |
| Icons | Lucide React |

### Setup

**Prerequisites:** Node.js v18+

```bash
cd CS432_Track1_Group10_A2/Module_B/app

npm install
```

Create a `.env` file (copy from `.env.example`):

```env
PORT=3000
NODE_ENV=development
```

The SQLite database (`hostel.db`) is initialised automatically on first run. To seed data manually:

```bash
sqlite3 hostel.db < hostel.sql
sqlite3 hostel.db < seed.sql
```

### Running the Application

```bash
# Development (backend + Vite HMR)
npm run dev
```

Access at: [http://localhost:3000](http://localhost:3000)

```bash
# Production
npm run build
npm start
```

### Demo Credentials

Use the **Demo Accounts** button on the sign-in page to log in as Admin or Regular User.

### API Overview

All endpoints require a valid session cookie except `/api/auth/login`. RBAC is enforced per route:

| Middleware | Applied to | Behaviour |
|-----------|-----------|-----------|
| `requireAdmin` | Global admin endpoints | Returns 403 for any non-Admin role |
| `requireOwnershipOrAdmin` | Member-scoped endpoints | Blocks access to another user's data; returns 403 |

Key route groups: `/api/auth`, `/api/members`, `/api/allocations`, `/api/complaints`, `/api/visitors`, `/api/maintenance`, `/api/rooms`, `/api/fees`, `/api/furniture`, `/api/scans`, `/api/hostels`

### Optimisation Summary

8 targeted SQL indexes applied after query pattern analysis:

| Index | Table | Columns |
|-------|-------|---------|
| `idx_members_list` | Member | IdentificationNumber, Email |
| `idx_allocations_full` | Allocation | CheckInDate DESC, IdentificationNumber, RoomID |
| `idx_rooms_status` | Room | HostelID |
| `idx_complaints_full` | Complaint | IdentificationNumber |
| `idx_visitors_full` | Visitor | IdentificationNumber |
| `idx_maintenance_full` | MaintenanceRequest | RequestedBy |
| `idx_fees_full` | FeePayment | MemberID, PaymentDate DESC |
| `idx_furniture_member` | FurnitureItem | MemberID |

Results across 33 endpoints: 76% improved, max improvement +47.1%, average improvement +29.4%, rows examined per dashboard query reduced by >99%.

Full benchmarking analysis with before/after graphs, EXPLAIN QUERY PLAN outputs, and statistical breakdown is in `Optimisation_Implementation_Report.ipynb`.

---

## Team

| Member | Contribution |
|--------|-------------|
| Vipul Sunil Patil | Schema design, indexing strategy, benchmarking |
| Sai | Security implementation, RBAC, report writing |
| Daksh Jain | API profiling, performance data collection |
| Daksh Dave | Data seeding, EXPLAIN analysis, documentation |
| Harshit | Index creation, query optimisation, verification |
