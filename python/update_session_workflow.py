#!/usr/bin/env python3
"""
Update Session Workflow Instructions
Adds directory mapping to session end procedures
"""

import os
from datetime import datetime

def update_development_plan():
    """Update the development plan with session workflow instructions"""
    dev_plan_path = 'development_plan.md'
    
    if not os.path.exists(dev_plan_path):
        print("⚠️  development_plan.md not found")
        return False
    
    with open(dev_plan_path, 'r') as f:
        content = f.read()
    
    # Session workflow section to add
    session_workflow = """
---

## Session Workflow

### Session Start Procedure
1. **Read Session Summary**: Review `Session summaries` in project knowledge to understand current status
2. **Map Project Structure**: Run `python python/directory_mapper.py` to see current file structure
3. **Ask for Required Files**: Request specific files based on current phase and issues
4. **Set Session Goals**: Identify 2-3 specific tasks to complete this session

### During Session
- **Commit Frequently**: Make commits after each working feature
- **Test Changes**: Validate functionality before moving to next task
- **Document Issues**: Note any blockers or problems encountered
- **Update Status**: Keep track of what's working vs. what needs fixing

### Session End Procedure
1. **Run Structure Mapper**: Execute `python python/directory_mapper.py` to generate current project state
2. **Create Session Summary**: Document what was completed, current status, and next priorities
3. **Upload Structure Output**: Add the directory mapper output to project knowledge
4. **Commit Final State**: Ensure all changes are committed to Git
5. **Update Project Knowledge**: Replace session summary with current status

### File Management
- **Always use relative paths** from project root when requesting files
- **Check structure first** before asking for files that might not exist
- **Upload key files** to project knowledge when making significant changes
- **Keep project_structure.json** updated for reference

"""
    
    # Find where to insert the session workflow
    if "## Development Workflow" in content:
        # Insert after the existing Development Workflow section
        parts = content.split("## Development Workflow")
        if len(parts) >= 2:
            # Find the next ## section or end of file
            after_workflow = parts[1]
            next_section_idx = after_workflow.find("\n## ")
            if next_section_idx != -1:
                # Insert before next section
                updated_content = (parts[0] + "## Development Workflow" + 
                                 after_workflow[:next_section_idx] + 
                                 session_workflow +
                                 after_workflow[next_section_idx:])
            else:
                # Insert at end
                updated_content = parts[0] + "## Development Workflow" + after_workflow + session_workflow
    else:
        # Add at the end
        updated_content = content + session_workflow
    
    with open(dev_plan_path, 'w') as f:
        f.write(updated_content)
    
    return True

def create_session_workflow_file():
    """Create a dedicated session workflow file"""
    workflow_content = """# Session Workflow Guide

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
- [ ] ✅ **Completed**: What was finished and working
- [ ] 🔧 **Current Status**: What's in progress or partially working  
- [ ] 🎯 **Next Session Priorities**: Top 3 tasks for next time
- [ ] 📁 **Files Ready**: What files are implemented/available
- [ ] 🚨 **Issues**: Any blockers or problems to address

### 3. Update Project Knowledge
- [ ] Upload directory mapper output
- [ ] Replace previous session summary
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
- ✅ **Do**: Use relative paths like `frontend/src/components/Login.tsx`
- ❌ **Don't**: Assume file locations without checking structure
- ✅ **Do**: Ask for specific files based on current issues
- ❌ **Don't**: Request large batches of files at once

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
"""
    
    with open('SESSION_WORKFLOW.md', 'w') as f:
        f.write(workflow_content)
    
    return True

def update_readme():
    """Add session workflow reference to README"""
    readme_path = 'README.md'
    
    if not os.path.exists(readme_path):
        print("⚠️  README.md not found")
        return False
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Add reference to session workflow in development section
    workflow_ref = """
### Development Sessions

For consistent development workflow, see [SESSION_WORKFLOW.md](SESSION_WORKFLOW.md) which includes:
- Session start/end checklists
- Project structure mapping procedures  
- File management guidelines
- Phase-specific workflows
- Troubleshooting common issues

**Quick Start for Each Session:**
```bash
# 1. Map current project structure
python python/directory_mapper.py

# 2. Start development based on current phase
# 3. End session with updated structure and summary
```
"""
    
    # Find a good place to insert this - after setup instructions
    if "## 🔧 Setup Instructions" in content and "## 🎮 Game Rules" in content:
        parts = content.split("## 🎮 Game Rules")
        updated_content = parts[0] + workflow_ref + "\n## 🎮 Game Rules" + parts[1]
    else:
        # Add before the end
        updated_content = content + workflow_ref
    
    with open(readme_path, 'w') as f:
        f.write(updated_content)
    
    return True

def update_changelog():
    """Update changelog with session workflow addition"""
    changelog_path = 'CHANGELOG.md'
    
    if not os.path.exists(changelog_path):
        print("⚠️  CHANGELOG.md not found")
        return False
    
    try:
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        # Add entry to unreleased section
        script_entry = f"""- **Python Script**: Session workflow update - Added comprehensive session management procedures and directory mapping to development workflow ({datetime.now().strftime('%Y-%m-%d')})"""
        
        if '### Added' in content and '## [Unreleased]' in content:
            # Find the Added section under Unreleased
            lines = content.split('\n')
            new_lines = []
            in_unreleased = False
            added_entry = False
            
            for line in lines:
                new_lines.append(line)
                if '## [Unreleased]' in line:
                    in_unreleased = True
                elif line.startswith('## [') and '## [Unreleased]' not in line:
                    in_unreleased = False
                elif in_unreleased and '### Added' in line and not added_entry:
                    new_lines.append(script_entry)
                    added_entry = True
            
            with open(changelog_path, 'w') as f:
                f.write('\n'.join(new_lines))
            
            return True
    except Exception as e:
        print(f"⚠️  Error updating changelog: {e}")
        return False

def main():
    """Main function to update session workflow instructions"""
    print("🔄 Updating session workflow instructions...")
    
    # Create the dedicated session workflow file
    if create_session_workflow_file():
        print("✅ Created SESSION_WORKFLOW.md with comprehensive session procedures")
    
    # Update development plan
    if update_development_plan():
        print("✅ Updated development_plan.md with session workflow reference")
    
    # Update README
    if update_readme():
        print("✅ Updated README.md with session workflow reference")
    
    # Update changelog
    if update_changelog():
        print("✅ Updated CHANGELOG.md with session workflow entry")
    
    print("\n🎯 Session Workflow Instructions Added!")
    print("\n📋 New Session End Procedure:")
    print("   1. Run: python python/directory_mapper.py")
    print("   2. Create session summary with status")
    print("   3. Upload directory mapper output to project knowledge")
    print("   4. Replace previous session summary")
    print("   5. Commit all changes to Git")
    print("\n📖 See SESSION_WORKFLOW.md for complete guidelines")

if __name__ == "__main__":
    main()
