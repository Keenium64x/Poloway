# Poloway Onboarding Flow

The main onboarding module is `Poloway System Onboarding`.

It is designed to move an owner or stable manager through the system in this order:

1. Foundation horse data
2. Horse care records
3. Inventory and vendors
4. Groom task setup
5. Money entry
6. Receipt upload
7. Financial review

## Trigger Conditions

The onboarding panel appears when all of these are true:

- `System Settings.enable_onboarding` is enabled.
- The user has `Horse Owner`, `Stable Manager`, or `System Manager`.
- `Module Onboarding > Poloway System Onboarding` is not complete.
- The current workspace includes an onboarding block named `Poloway System Onboarding`.

The onboarding is added to:

- `Poloway`
- `Owner Dashboard`
- `Workspace Sidebar > Poloway` as `module_onboarding`

Each setup action that needs explanation launches a form tour as part of the onboarding step.

## Step Order

### 1. Create the first horse profile

Action: `Create Entry`

Reference DocType: `Horse`

Form Tour: `Horse Profile Basics`

Trigger behavior:

- The onboarding step opens the full Horse form.
- Because `show_form_tour = 1`, Frappe starts `Horse Profile Basics`.

### 2. Tour feeding records

Action: `Show Form Tour`

Reference DocType: `Horse Feeding Record`

Form Tour: `Horse Feeding Record Basics`

Trigger behavior:

- The onboarding step opens a new feeding record.
- Frappe starts the feeding form tour.

### 3. Tour training records

Action: `Show Form Tour`

Reference DocType: `Horse Training Record`

Form Tour: `Horse Training Record Basics`

### 4. Tour medical records

Action: `Show Form Tour`

Reference DocType: `Horse Medical Record`

Form Tour: `Horse Medical Record Basics`

### 5. Review horse performance

Action: `View Report`

Report: `Horse Performance Summary`

This shows training, chukkers, issues, medical due items, expenses, and readiness score.

### 6. Review medical follow-ups

Action: `View Report`

Report: `Horse Compliance Alerts`

This catches upcoming and overdue medical follow-ups.

### 7. Create inventory items

Action: `Create Entry`

Reference DocType: `Item`

Form Tour: `Item Basics`

This is where feed, medicine, tack, supplies, services, and valued items are created.

### 8. Create vendors

Action: `Create Entry`

Reference DocType: `Vendor`

Form Tour: `Vendor Basics`

This prepares suppliers, vets, farriers, transport providers, horse sellers, buyers, and service providers.

### 9. Create the groom task template

Action: `Create Entry`

Reference DocType: `Task Template`

Form Tour: `Task Template Basics`

This creates the daily routine that generates groom tasks.

### 10. Configure task generation

Action: `Show Form Tour`

Reference DocType: `Task Schedule Settings`

Form Tour: `Task Schedule Settings Basics`

This sets the default template, default groom, auto generation, and day overrides.

### 11. Open the groom task board

Action: `Go to Page`

Path: `/app/task/view/kanban/Whiteboard`

This shows the groom-facing task board.

### 12. Create a manual transaction

Action: `Create Entry`

Reference DocType: `Transaction Input`

Form Tour: `Transaction Input Basics`

This teaches the single central entry point for ledger creation.

### 13. Review money flow

Action: `View Report`

Report: `Money Flow Summary`

This shows income, outflow, and net cash flow.

### 14. Upload receipts

Action: `Create Entry`

Reference DocType: `Receipt Import`

Form Tour: `Receipt Upload Basics`

This is the receipt OCR/AI workflow. It supports one or multiple files, extracted lines, vendor matching, item matching, and transaction creation.

### 15. Review the ledger

Action: `View Report`

Report: `Financial Ledger`

This is the immutable posted financial movement view.

