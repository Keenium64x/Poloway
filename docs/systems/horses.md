# Horse System

The horse system is the foundation of Poloway. A horse profile stores the current state of the horse, while feeding, training, and medical records are separate transaction-style records that can be filtered and reported.

## Main DocTypes

- `Horse`: identity, physical details, registration, location, handling, playing state, availability, and ownership.
- `Horse Feeding Record`: one feeding event for one horse.
- `Horse Training Record`: one training session or planned training outcome for one horse.
- `Horse Medical Record`: one medical occurrence, treatment, observation, procedure, or follow-up for one horse.

## Reports

- `Horse Performance Summary`: owner-facing performance and care summary.
- `Horse Compliance Alerts`: upcoming or overdue medical follow-up records.
- `Horse Feeding Records`: filterable feeding history.
- `Horse Training Records`: filterable training history.
- `Horse Medical Records`: filterable medical history.

## Recommended Flow

1. Create the `Horse`.
2. Add registration, location, handling, playing, availability, and ownership details.
3. Use the record buttons or reports to view related feeding, training, and medical history.
4. Add feeding, training, and medical records as separate entries.
5. Review `Horse Performance Summary` and `Horse Compliance Alerts` from the owner view.

## Onboarding

Use `Poloway System Onboarding` from the Poloway or Owner workspace when available.

If the onboarding panel is not visible, check:

- `System Settings > Enable Onboarding` is enabled.
- The user has `Horse Owner`, `Stable Manager`, or `System Manager`.
- `Module Onboarding > Poloway System Onboarding` is not complete.
- The workspace content includes an onboarding block named `Poloway System Onboarding`.

Form tours can always be opened manually from the `Form Tour` list by opening the relevant tour and clicking **Show Tour**.
