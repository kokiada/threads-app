# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Threads automated posting application built with Next.js 15 and React 19. The main application consists of a dashboard interface for managing multiple Threads accounts and scheduling posts. This is a modern React application using TypeScript and Tailwind CSS with shadcn/ui components.

**Key Project Structure:**
- Main application code is in `/threads-app/` directory
- Single-page React component: `threads-manager.tsx` contains the entire dashboard interface
- Uses Next.js App Router with the main page at `app/page.tsx`
- UI components from shadcn/ui library in `components/ui/`

## Development Commands

**Working Directory:** Always work from `/threads-app/` directory

```bash
# Start development server with Turbo
npm run dev

# Build the application
npm run build

# Start production server
npm start

# Run ESLint for code quality
npm run lint
```

## Architecture Notes

**Component Architecture:**
- Main application is a single large component (`ThreadsManager`) with internal state management
- Uses React hooks for state management (no external state library)
- Mobile-first responsive design with desktop adaptations
- Modal-based interactions for creating posts and adding accounts

**UI Framework:**
- Tailwind CSS for styling
- shadcn/ui component library (Radix UI based)
- Lucide React for icons
- Responsive design with mobile sidebar overlay and desktop fixed sidebar

**Key Features Implemented:**
- Dashboard with account overview, scheduled posts, and recent posts
- Account management interface
- Post creation modal with account selection and scheduling
- Responsive navigation (mobile bottom nav + desktop sidebar)
- Placeholder screens for schedule, analytics, and settings

**Data Structure:**
- Currently uses mock data arrays for accounts, posts, and schedules
- No backend integration yet - ready for API integration
- Form state managed with React useState hooks

## Development Notes

- Application uses Japanese language in the UI
- Mobile-optimized with touch-friendly interactions
- FAB (Floating Action Button) for quick post creation
- Supports both immediate and scheduled posting (UI only)
- Account status tracking (active/expired tokens)