'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Briefcase,
  ShieldCheck,
  Mail,
  Users,
  Download,
  BarChart3,
  Database,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bell,
  User,
  Activity,
  LogOut,
  Moon,
  Sun,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Jobs', href: '/dashboard/jobs', icon: Briefcase },
  { name: 'Verification', href: '/dashboard/verification', icon: ShieldCheck },
  { name: 'Contacts', href: '/dashboard/contacts', icon: Mail },
  { name: 'Outreach', href: '/dashboard/outreach', icon: Users },
  { name: 'Exports', href: '/dashboard/exports', icon: Download },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Sources', href: '/dashboard/sources', icon: Database },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const pathname = usePathname()
  const { user, signOut } = useAuth()

  // Handle sidebar transition with CSS
  useEffect(() => {
    const sidebar = document.querySelector('[data-sidebar]')
    if (sidebar) {
      sidebar.style.transition = 'width 0.3s ease, transform 0.3s ease'
    }
  }, [collapsed, mobileOpen])

  return (
    <div className="min-h-screen bg-background flex">
      <aside
        data-sidebar
        className={cn(
          'fixed left-0 top-0 z-40 h-screen bg-surface border-r border-border transition-all duration-300 flex flex-col',
          collapsed ? 'w-20' : 'w-72',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          {!collapsed && (
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center">
                <Activity className="w-5 h-5 text-background" />
              </div>
              <span className="font-bold text-lg text-primary-text">JobShield</span>
            </Link>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-2 rounded-xl text-secondary-text hover:text-primary-text hover:bg-surface-secondary transition-colors lg:hidden"
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-1" role="navigation" aria-label="Main navigation">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'sidebar-link',
                  isActive && 'sidebar-link-active'
                )}
                onClick={() => setMobileOpen(false)}
              >
                <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <div className={cn('transition-all duration-200 overflow-hidden', collapsed ? 'h-0 opacity-0' : 'h-auto opacity-100')}>
            <div className="space-y-2">
              <button className="sidebar-link w-full justify-start">
                <Moon className="w-5 h-5" />
                <span>Appearance</span>
              </button>
              <hr className="border-border" />
              <button className="sidebar-link w-full justify-start text-red-400 hover:bg-red-600/10" onClick={() => signOut()}>
                <LogOut className="w-5 h-5" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-background/50 lg:hidden transition-opacity duration-300"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <div className={cn('flex-1 flex flex-col min-w-0 transition-all duration-300', collapsed ? 'lg:pl-20' : 'lg:pl-72')}>
        <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-6 sticky top-0 z-20">
          <button
            className="lg:hidden p-2 rounded-xl text-secondary-text hover:text-primary-text hover:bg-surface-secondary"
            onClick={() => setMobileOpen(true)}
          >
            <LayoutDashboard className="w-5 h-5" />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-4">
            <button className="relative p-2 rounded-xl text-secondary-text hover:text-primary-text hover:bg-surface-secondary transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full" />
            </button>

            <div className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-xl bg-surface-secondary border border-border">
              <User className="w-5 h-5 text-secondary-text" />
              <span className="text-sm text-primary-text">{user?.name || user?.email}</span>
            </div>

            <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center">
              <Activity className="w-4 h-4 text-background" />
            </div>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}