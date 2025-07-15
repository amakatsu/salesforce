# CLAUDE.md

必ず日本語で回答してください
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Salesforce DX project focused on Lightning Web Components (LWC) development, specifically demonstrating advanced data table implementations and custom table components. The project uses Japanese language in documentation and comments, targeting enterprise-level Japanese business applications.

## Development Commands

### Salesforce CLI Commands

- **Deploy to scratch org**: `sfdx force:source:push`
- **Pull from scratch org**: `sfdx force:source:pull`
- **Create scratch org**: `sfdx force:org:create -s -f config/project-scratch-def.json`
- **Open scratch org**: `sfdx force:org:open`
- **Deploy to non-source-tracked org**: `sfdx force:source:deploy -p force-app`
- **Retrieve from non-source-tracked org**: `sfdx force:source:retrieve -p force-app`

### Project Structure Commands

- **Run SOQL queries**: Use files in `scripts/soql/` directory
- **Execute Apex**: Use files in `scripts/apex/` directory

## Architecture and Code Patterns

### Component Categories

**1. Custom Data Tables (`customDatatable*`)**

- Advanced lightning-datatable implementations with custom cell types
- Features picklist cells (`picklistCell`), boolean editing, and date inputs
- Uses draft values pattern for batch editing and saving
- Mock data generation pattern with 100+ rows for performance testing

**2. Tree Grid Components (`editableTreeGrid*`)**

- Hierarchical data representation with expand/collapse functionality
- State management service pattern (`editableTreeGridState.js`)
- Supports inline editing with field-level edit permissions
- Change tracking and highlighting system for modified data

**3. Table Harness Components (`customTableHarness`, `customTableWithTh`)**

- Testing and demonstration containers for other components
- Manual HTML table implementation using SLDS classes
- Alternative to lightning-datatable for custom styling needs

### Key Patterns

**State Management**

- Reactive properties using `@track` decorator
- Service-based state management for complex components (tree grid)
- Draft values pattern for batched edits before save

**Data Handling**

- Mock data generation functions for development/testing
- Japanese business terminology (支店/Branch, 職場/Workplace, 審査結果/Review Result)
- Comprehensive field types: text, boolean, date, picklist

**Custom Cell Types**

- `picklistCell` type for dropdown selections in data tables
- Custom boolean and date cell implementations
- TypeAttributes pattern for passing configuration to custom cells

## Component File Structure

Each LWC component follows standard structure:

- `componentName.js` - Controller logic and reactive properties
- `componentName.html` - Template with Lightning base components
- `componentName.js-meta.xml` - Metadata and target configurations
- `componentName.css` - Component-specific styling (when present)

## Development Notes

- Project uses Salesforce API version 47.0
- Default package directory is `force-app`
- No Node.js package.json - pure Salesforce DX project
- Components designed for both App Builder and standalone deployment
- Focus on enterprise data management use cases

## Business Context

Components target Japanese financial/credit management workflows with fields like:

- 与信番号 (Credit Number)
- 審査結果 (Review Result)
- 月末与信決済 (Month-end Credit Settlement)
- 実査権限 (Investigation Authority)

## Testing Strategy

- Mock data generation for consistent testing
- Harness components for isolated component testing
- Use scratch orgs for development and testing iterations
