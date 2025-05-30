# Changelog

All notable changes to the Codenames Web App project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [0.1.0] - 2025-05-29

### Added
- Complete project structure setup with frontend, backend, and shared directories
- Docker configuration for PostgreSQL and Redis development databases
- TypeScript configurations with strict settings for both frontend and backend
- Package.json files with all necessary dependencies for React and Node.js
- Prisma ORM setup with PostgreSQL schema for users, game rooms, and game state
- Vite configuration for React frontend with path aliases
- Tailwind CSS setup with custom game colors
- Basic Express server with Socket.io integration
- Environment configuration templates
- Git ignore files and Docker ignore configuration
- Basic React components structure and routing setup
- JWT authentication foundation
- Rate limiting and security middleware setup

### Changed
- N/A (Initial setup)

### Security
- Added Helmet middleware for security headers
- Implemented rate limiting for API endpoints
- Set up CORS configuration
- JWT token structure for authentication

---

## Python Scripts Run




- `python/setup_project.py` - Initial project structure and configuration setup (2025-05-29)
- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials (2025-05-29)
- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials (2025-05-29)
- `python/fix_prisma_connection.py` - Fixed Prisma database connection issues (2025-05-29)
- `python/check_port_conflicts.py` - Checked for port conflicts and created alternative configuration (2025-05-29)

---


## Release Guidelines

### Version Numbering
- **MAJOR** version: Incompatible API changes or major feature overhauls
- **MINOR** version: New functionality in a backwards compatible manner
- **PATCH** version: Backwards compatible bug fixes

### Change Categories
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

### Development Phases
- **v0.1.0** - Basic game setup and local multiplayer
- **v0.2.0** - WebSocket integration and real-time play
- **v0.3.0** - Room management and player matching
- **v0.4.0** - UI polish and responsive design
- **v0.5.0** - Deployment preparation
- **v1.0.0** - First production release




## Development Changelog

<!-- When you're ready to start development, move items from Unreleased to a new version section -->

### Example Entry Format:
<!--
## [0.1.0] - 2025-05-29

### Added
- Basic React frontend with TypeScript and Vite setup
- Express backend with Socket.io integration
- PostgreSQL database with Prisma ORM
- Core game state management with Context API
- Basic game board component and card system
- JWT authentication system
- Room creation and joining functionality

### Changed
- Updated package.json dependencies to latest versions

### Fixed
- Fixed TypeScript configuration for shared types

### Security
- Added input validation with Zod schemas
-->




## Future Changelog Template

<!--
Copy this template when adding new releases:

## [Version] - YYYY-MM-DD

### Added
- 

### Changed
- 

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- 

-->