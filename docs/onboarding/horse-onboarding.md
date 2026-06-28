# Horse Onboarding

Horse onboarding introduces the horse modelling system first, because every care record, task, medical history entry, and performance report depends on the horse record being clean.

## Native Records Created

The install hook creates these `Form Tour` records:

- `Horse Profile Basics`
- `Horse Feeding Record Basics`
- `Horse Training Record Basics`
- `Horse Medical Record Basics`

It is included in the broader `Poloway System Onboarding`, which also covers task setup, money entry, and receipt upload.

Horse-specific onboarding creates:

- `Module Onboarding`: `Poloway System Onboarding`
- `Onboarding Step`: `Create the first horse profile`
- `Onboarding Step`: `Tour feeding records`
- `Onboarding Step`: `Tour training records`
- `Onboarding Step`: `Tour medical records`
- `Onboarding Step`: `Review horse performance`
- `Onboarding Step`: `Review medical follow-ups`

## Trigger Conditions

### Horse Profile Basics

Reference DocType: `Horse`

Trigger paths:

- Open `Form Tour > Horse Profile Basics` and click **Show Tour**.
- Open the `Poloway System Onboarding` panel and click **Create Horse**.
- When launched from the onboarding step, Frappe opens the full `Horse` form and starts the tour.

Important setting:

- `first_document = 1`

This means the Form Tour document's **Show Tour** action opens the first existing horse if one exists. If there is no horse yet, it opens a new horse form.

### Horse Feeding Record Basics

Reference DocType: `Horse Feeding Record`

Trigger paths:

- Open `Form Tour > Horse Feeding Record Basics` and click **Show Tour**.
- Open the `Poloway System Onboarding` panel and click **Start Feeding Tour**.

This tour opens a new feeding record when launched from onboarding.

### Horse Training Record Basics

Reference DocType: `Horse Training Record`

Trigger paths:

- Open `Form Tour > Horse Training Record Basics` and click **Show Tour**.
- Open the `Poloway System Onboarding` panel and click **Start Training Tour**.

This tour opens a new training record when launched from onboarding.

### Horse Medical Record Basics

Reference DocType: `Horse Medical Record`

Trigger paths:

- Open `Form Tour > Horse Medical Record Basics` and click **Show Tour**.
- Open the `Poloway System Onboarding` panel and click **Start Medical Tour**.

This tour opens a new medical record when launched from onboarding.

## Horse Profile Tour

The horse profile tour teaches:

- `Name`: the everyday stable name used by people linking horses.
- `Height (m)` and `Weight (kg)`: metric physical details.
- `Registration Number`: passport, registration, microchip, and authority details.
- `Current Location`: where the horse is kept now.
- `Temperament`: handling notes and special instructions.
- `Playing Status`: playing status, position, handicap, and notes.
- `Availability Status`: available, unavailable, reserved, sold, or leased.
- `Ownership`: owner relationship records.
- `Medical Records Report`: the pattern for transaction-style linked records.

## Feeding Tour

The feeding record tour teaches:

- Choose the horse.
- Record date and time.
- Select a food item.
- Record quantity and unit.
- Add notes for refusals, substitutions, appetite changes, or owner review.

## Training Tour

The training record tour teaches:

- Choose the horse.
- Use a training template when applicable.
- Record work type, duration, and intensity.
- Capture outcome.
- Use ratings for speed, responsiveness, and mouth sensitivity.
- Add a concise session note.

## Medical Tour

The medical record tour teaches:

- Choose the horse.
- Pick a medical record type.
- Link the responsible person, not only a veterinarian.
- Write a short summary.
- Capture medication, materials, dosage, or quantity.
- Add a next due date for follow-up.
- Add detailed notes.

## Owner Review Steps

The onboarding also links to:

- `Horse Performance Summary`
- `Horse Compliance Alerts`

These reports are used after setup to review horse readiness, training, chukkers, open issues, medical due items, expenses, and follow-ups.
