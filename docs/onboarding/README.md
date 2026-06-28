# Poloway Onboarding

This folder documents the guided onboarding that is created by `polomanagement/install.py`.

## Trigger Conditions

Poloway uses native Frappe onboarding records:

- `Form Tour`: field-by-field popovers on a DocType form.
- `Onboarding Step`: checklist actions that can create records, open reports, or launch a form tour.
- `Module Onboarding`: a grouped onboarding checklist shown by a workspace/sidebar when onboarding is enabled.

Onboarding is enabled during migration by setting `System Settings.enable_onboarding = 1`.

### Form Tour Triggers

Form tours are attached to a `reference_doctype`.

- They can be launched from the `Form Tour` document using **Show Tour**.
- They can be launched from an `Onboarding Step` with action `Show Form Tour`.
- If `first_document = 1`, the Form Tour **Show Tour** action opens the first existing document for that DocType, or a new document if none exists.
- For onboarding steps that use `Show Form Tour`, Frappe opens a new document form for non-single doctypes, then starts the configured tour.

### Workspace Onboarding Triggers

The workspace content includes an `onboarding` block named `Poloway System Onboarding`.

It is expected to show when:

- System onboarding is enabled.
- The logged-in user has one of the allowed roles.
- The module onboarding is not marked complete.
- The workspace content includes the onboarding block.

Allowed roles for the horse onboarding are:

- Horse Owner
- Stable Manager
- System Manager

The Poloway sidebar also points `module_onboarding` to `Poloway System Onboarding`.

## Current Onboarding Sets

- [Poloway Onboarding Flow](poloway-onboarding.md)
- [Horse Onboarding](horse-onboarding.md)
