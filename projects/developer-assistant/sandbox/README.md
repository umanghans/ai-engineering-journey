# Developer Assistant Sandbox

This directory contains a small sample repository used to test the Developer Assistant's repository-aware tools.

The assistant is restricted to this directory when searching and reading files, providing a controlled environment for demonstrating both repository inspection and filesystem security.

## Files

### `pricing.py`

Contains sample pricing logic, including:

- `TAX_RATE`
- Subtotal calculation
- Tax calculation
- Total-price calculation

The Developer Assistant can locate `TAX_RATE`, inspect the implementation, and use the discovered value when answering questions or performing calculations.

### `users.py`

Contains sample user data and a helper function for retrieving users by ID.

This provides additional repository content for testing code search and file inspection beyond the pricing example.

## Purpose

The sandbox is intentionally small so that agent behavior is easy to inspect.

It can be used to demonstrate:

- Searching a repository for symbols and configuration values
- Reading source files discovered through search
- Reasoning across repository contents
- Combining repository information with other tools
- Rejecting attempts to read files outside the allowed directory

The sandbox contains only sample data and code and is not part of a production application.