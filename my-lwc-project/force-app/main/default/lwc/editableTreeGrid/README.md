# Editable Tree Grid Component

A reusable Lightning Web Component (LWC) that provides an editable tree grid with hierarchical data display and inline editing capabilities.

## Features

- Hierarchical data display with expand/collapse functionality
- Inline editing of various field types (text, number, date, checkbox, dropdown)
- Configurable columns with different input types
- Customizable editability rules
- Change highlighting
- Draft changes tracking
- Save and reset functionality
- Event dispatching for integration

## Usage

```html
<c-editable-tree-grid
  title="My Tree Grid"
  save-button-label="Save Changes"
  reset-button-label="Discard Changes"
  columns="{columns}"
  data="{data}"
  id-field="id"
  children-field="children"
  editable-field-fn="{checkEditability}"
  show-draft-json="true"
  onchange="{handleChange}"
  onsave="{handleSave}"
  onreset="{handleReset}"
></c-editable-tree-grid>
```

## Configuration

### Properties

| Property           | Type     | Description                             | Default               |
| ------------------ | -------- | --------------------------------------- | --------------------- |
| `title`            | String   | Title for the component                 | "Editable Tree Table" |
| `saveButtonLabel`  | String   | Label for the save button               | "Save"                |
| `resetButtonLabel` | String   | Label for the reset button              | "Reset"               |
| `columns`          | Array    | Column definitions                      | []                    |
| `data`             | Array    | Tree data structure                     | []                    |
| `idField`          | String   | Field name for unique identifier        | "id"                  |
| `childrenField`    | String   | Field name for children array           | "children"            |
| `editableFieldFn`  | Function | Function to determine field editability | undefined             |
| `showDraftJson`    | Boolean  | Whether to show draft changes as JSON   | true                  |

### Column Definition

Each column in the `columns` array should have the following structure:

```javascript
{
    fieldName: 'fieldName',  // API name of the field in the data
    label: 'Column Label',   // Display label for the column
    type: 'text',            // Input type: 'text', 'number', 'date', 'checkbox', 'combobox'
    editable: true,          // Whether the field is editable (boolean or function)
    options: [               // Options for combobox type (optional)
        { label: 'Option 1', value: 'option1' },
        { label: 'Option 2', value: 'option2' }
    ]
}
```

### Data Structure

The `data` property should be an array of objects with a hierarchical structure:

```javascript
[
  {
    id: "1",
    name: "Parent 1",
    status: "Active",
    children: [
      {
        id: "1.1",
        name: "Child 1.1",
        status: "Active"
      },
      {
        id: "1.2",
        name: "Child 1.2",
        status: "Inactive"
      }
    ]
  },
  {
    id: "2",
    name: "Parent 2",
    status: "Inactive"
  }
];
```

### Editability Function

The `editableFieldFn` property allows you to define complex rules for field editability:

```javascript
function checkEditability(record, fieldName) {
  // Example: Only allow editing active records
  if (record.status === "Inactive") {
    return false;
  }

  // Example: Don't allow editing of specific fields for certain records
  if (record.type === "Special" && fieldName === "name") {
    return false;
  }

  return true;
}
```

## Events

| Event    | Detail                         | Description                            |
| -------- | ------------------------------ | -------------------------------------- |
| `change` | `{ id, field, value, record }` | Fired when a field value changes       |
| `save`   | `{ data }`                     | Fired when the save button is clicked  |
| `reset`  | none                           | Fired when the reset button is clicked |

## CSS Customization

The component uses the following CSS classes that can be customized:

- `.changed-cell` - Highlights changed cells
- `.indent-{level}` - Controls indentation for tree levels
- `.checkbox-column` - Centers checkbox columns

## Example

```javascript
import { LightningElement, track } from "lwc";

export default class MyComponent extends LightningElement {
  @track columns = [
    { fieldName: "name", label: "Name", type: "text" },
    {
      fieldName: "status",
      label: "Status",
      type: "combobox",
      options: [
        { label: "Active", value: "Active" },
        { label: "Inactive", value: "Inactive" }
      ]
    },
    { fieldName: "joinDate", label: "Join Date", type: "date" },
    { fieldName: "active", label: "Active", type: "checkbox" }
  ];

  @track data = [
    {
      id: "1",
      name: "Department A",
      status: "Active",
      joinDate: "2020-01-01",
      active: true,
      children: [
        {
          id: "1.1",
          name: "Team A1",
          status: "Active",
          joinDate: "2020-02-15",
          active: true
        }
      ]
    }
  ];

  checkEditability(record, fieldName) {
    // Example: Inactive records can't be edited
    if (!record.active && fieldName !== "active") {
      return false;
    }
    return true;
  }

  handleChange(event) {
    console.log("Field changed:", event.detail);
  }

  handleSave(event) {
    console.log("Saved data:", event.detail.data);
  }
}
```
