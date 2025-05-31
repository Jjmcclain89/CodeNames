# Session Workflow Guide

This guide outlines the recommended workflow for development sessions on the Codenames Web App project.

## Session Start Checklist

### 1. Review Previous Session
- [ ] Read the latest session summary in project knowledge
- [ ] Check current phase status (Phase 0-4)
- [ ] Note any outstanding issues or blockers

### 2. Map Current Project State
```bash
python python/directory_mapper.py
```
- [ ] Review the generated project structure
- [ ] Identify what files exist vs. what's expected
- [ ] Note any new or changed files since last session

### 3. Request Necessary Files
- [ ] Use **relative paths** from project root
- [ ] Ask for files based on current issues, not assumptions
- [ ] Focus on files relevant to current phase goals
- [ ] It's better to ask for too many files than too few

### 4. Set Session Objectives
- [ ] Define 2-3 specific, achievable goals
- [ ] Prioritize based on current phase requirements
- [ ] Note any dependencies or prerequisites

## During Development

### Best Practices
- **Commit Early, Commit Often**: Make commits after each working feature
- **Test Continuously**: Validate changes with multiple browser windows
- **Document Problems**: Note issues in session summary as they arise
- **Stay Focused**: Complete current phase before moving to next

### Debugging Approach
1. **Reproduce the Issue**: Verify the problem exists
2. **Check Console Logs**: Both browser and backend console
3. **Verify Configuration**: Environment variables, ports, CORS
4. **Test Step by Step**: Isolate the failing component
5. **Fix and Validate**: Confirm fix works end-to-end

## Session End Checklist

### 1. Generate Current State
```bash
python python/directory_mapper.py
```
- [ ] Review what was accomplished
- [ ] Note current project structure
- [ ] Save output for next session

### 2. Document Session Results
Create a session summary with:
- [ ] [DONE] **Completed**: What was finished and working
- [ ] [WIP] **Current Status**: What's in progress or partially working  
- [ ] [NEXT] **Next Session Priorities**: Top 3 tasks for next time
- [ ] [FILES] **Files Ready**: What files are implemented/available
- [ ] [ISSUE] **Issues**: Any blockers or problems to address

### 3. Update Project Knowledge
- [ ] Upload directory mapper output
- [ ] Add to session summary history
- [ ] Add any new important files to project knowledge

### 4. Git Management
- [ ] Commit all changes with descriptive messages
- [ ] Push to remote repository
- [ ] Ensure working directory is clean

### 5. Prepare for Next Session
- [ ] Update development plan if phase completed
- [ ] Note specific files that will be needed next time
- [ ] Set realistic expectations for next session scope

## File Management Guidelines

### Requesting Files
- [YES] **Do**: Use relative paths like `frontend/src/components/Login.tsx`
- [NO] **Don't**: Assume file locations without checking structure
- [YES] **Do**: Ask for specific files based on current issues
- [NO] **Don't**: Request large batches of files at once

### Project Knowledge
- **Keep Updated**: Replace old session summaries with current status
- **Include Structure**: Upload directory mapper outputs regularly
- **Add Key Files**: Include important implementation files
- **Document Changes**: Note when files are added, modified, or moved

## Phase-Specific Workflows

### Phase 1: Socket Foundation
**Focus**: Real-time communication between browsers
- Start each session by testing socket connections
- Verify authentication flow works end-to-end
- Test with multiple browser windows/tabs
- Debug connection issues before adding features

### Phase 2: Core Game Logic  
**Focus**: Multiplayer Codenames gameplay
- Validate server-side game state management
- Test real-time synchronization of game events
- Ensure game rules are enforced properly
- Test edge cases (disconnections, invalid moves)

### Phase 3: Features & Polish
**Focus**: User experience and advanced features
- Test across different devices and browsers
- Optimize performance and responsiveness
- Add accessibility features
- Implement advanced room management

### Phase 4: Production Ready
**Focus**: Deployment and stability
- Security testing and hardening
- Performance optimization
- Deployment preparation
- Final testing with real users

## Troubleshooting Common Issues

### "File doesn't exist"
1. Run directory mapper to see current structure
2. Check if file was moved or renamed
3. Ask for correct file path based on actual structure

### "Can't connect to backend"
1. Verify backend server is running on correct port
2. Check CORS configuration in backend
3. Verify frontend API base URL matches backend
4. Check browser console for specific error messages

### "Socket connection fails"
1. Verify Socket.io versions match between frontend/backend
2. Check authentication flow and JWT token handling
3. Test with multiple browser windows
4. Check backend socket event handlers

### "Database connection errors"
1. Verify PostgreSQL is running
2. Check DATABASE_URL in .env file
3. Run `npm run db:migrate` to ensure schema is up to date
4. Test database connection with Prisma Studio

---

Remember: **Progress over perfection**. Complete one phase thoroughly before moving to the next. Each session should move the project forward in a measurable way.
