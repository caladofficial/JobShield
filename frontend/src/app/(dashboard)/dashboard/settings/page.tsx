'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import {
  User,
  Mail,
  Lock,
  Bell,
  Shield,
  Palette,
  Moon,
  Sun,
  Monitor,
  Save,
  Loader2,
  CheckCircle,
  Key,
  BarChart3,
  Trash2,
} from 'lucide-react'

const THEMES = [
  { value: 'system', label: 'System', icon: <Monitor className="w-4 h-4" /> },
  { value: 'light', label: 'Light', icon: <Sun className="w-4 h-4" /> },
  { value: 'dark', label: 'Dark', icon: <Moon className="w-4 h-4" /> },
]

export default function SettingsPage() {
  const { user, session } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [formData, setFormData] = useState({
    full_name: user?.name || '',
    email: user?.email || '',
    theme: 'dark',
    email_notifications: true,
    verification_alerts: true,
    weekly_digest: false,
  })

  const handleSave = async () => {
    setSaving(true)
    setSaved(false)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-primary-text">Settings</h1>
        <p className="text-secondary-text mt-1">Manage your account and preferences</p>
      </div>

      <Card>
        <div className="border-b border-border">
          <nav className="flex gap-1 p-1" role="tablist">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-accent/10 text-accent border border-accent/30'
                      : 'text-secondary-text hover:text-primary-text hover:bg-surface-secondary'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'profile' && (
            <ProfileTab formData={formData} setFormData={setFormData} user={user} saving={saving} saved={saved} onSave={handleSave} />
          )}
          {activeTab === 'notifications' && (
            <NotificationsTab formData={formData} setFormData={setFormData} />
          )}
          {activeTab === 'security' && (
            <SecurityTab />
          )}
          {activeTab === 'appearance' && (
            <AppearanceTab formData={formData} setFormData={setFormData} />
          )}
        </div>
      </Card>

      <Card>
        <h3 className="font-medium text-primary-text mb-4">Session Info</h3>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-secondary-text">User ID</dt>
            <dd className="font-mono text-primary-text mt-1">{user?.id}</dd>
          </div>
          <div>
            <dt className="text-secondary-text">Email</dt>
            <dd className="font-mono text-primary-text mt-1">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-secondary-text">Role</dt>
            <dd className="font-mono text-primary-text mt-1">{user?.role || 'user'}</dd>
          </div>
          <div>
            <dt className="text-secondary-text">Last Login</dt>
            <dd className="font-mono text-primary-text mt-1">{user?.last_login_at ? new Date(user.last_login_at).toLocaleString() : 'Never'}</dd>
          </div>
        </dl>
      </Card>

      <Card className="border-red-500/30">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium text-primary-text">Danger Zone</h3>
            <p className="text-secondary-text text-sm mt-1">Irreversible actions</p>
          </div>
          <Button variant="danger" onClick={() => alert('Account deletion not implemented in demo')}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Account
          </Button>
        </div>
      </Card>
    </div>
  )
}

function ProfileTab({ formData, setFormData, user, saving, saved, onSave }: any) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-20 h-20 rounded-2xl bg-accent/20 flex items-center justify-center">
          <User className="w-10 h-10 text-accent" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-primary-text">{formData.full_name || 'No name set'}</h3>
          <p className="text-secondary-text">{formData.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-secondary-text mb-1">Full Name</label>
          <Input
            value={formData.full_name}
            onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
            placeholder="Your name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary-text mb-1">Email</label>
          <Input
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            type="email"
            disabled
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button onClick={onSave} disabled={saving}>
          {saving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Saving...
            </>
          ) : saved ? (
            <>
              <CheckCircle className="w-4 h-4 mr-2" />
              Saved
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </>
          )}
        </Button>
      </div>
    </div>
  )
}

function NotificationsTab({ formData, setFormData }: any) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <label className="flex items-center justify-between cursor-pointer p-3 rounded-xl bg-surface-secondary/50 border border-border/50 hover:border-border transition-colors">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">Email Notifications</p>
              <p className="text-sm text-secondary-text">Receive email updates about your jobs</p>
            </div>
          </div>
          <input
            type="checkbox"
            checked={formData.email_notifications}
            onChange={(e) => setFormData(prev => ({ ...prev, email_notifications: e.target.checked }))}
            className="w-5 h-5 rounded border-border bg-surface-secondary text-accent focus:ring-accent"
          />
        </label>

        <label className="flex items-center justify-between cursor-pointer p-3 rounded-xl bg-surface-secondary/50 border border-border/50 hover:border-border transition-colors">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">Verification Alerts</p>
              <p className="text-sm text-secondary-text">Get notified when jobs need review</p>
            </div>
          </div>
          <input
            type="checkbox"
            checked={formData.verification_alerts}
            onChange={(e) => setFormData(prev => ({ ...prev, verification_alerts: e.target.checked }))}
            className="w-5 h-5 rounded border-border bg-surface-secondary text-accent focus:ring-accent"
          />
        </label>

        <label className="flex items-center justify-between cursor-pointer p-3 rounded-xl bg-surface-secondary/50 border border-border/50 hover:border-border transition-colors">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">Weekly Digest</p>
              <p className="text-sm text-secondary-text">Receive a weekly summary of your job activity</p>
            </div>
          </div>
          <input
            type="checkbox"
            checked={formData.weekly_digest}
            onChange={(e) => setFormData(prev => ({ ...prev, weekly_digest: e.target.checked }))}
            className="w-5 h-5 rounded border-border bg-surface-secondary text-accent focus:ring-accent"
          />
        </label>
      </div>
    </div>
  )
}

function SecurityTab() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
          <div className="flex items-center gap-3">
            <Lock className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">Change Password</p>
              <p className="text-sm text-secondary-text">Update your account password</p>
            </div>
          </div>
          <Button variant="secondary">Change</Button>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">Two-Factor Authentication</p>
              <p className="text-sm text-secondary-text">Add an extra layer of security</p>
            </div>
          </div>
          <Button variant="secondary">Enable</Button>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
          <div className="flex items-center gap-3">
            <Key className="w-5 h-5 text-secondary-text" />
            <div>
              <p className="font-medium text-primary-text">API Keys</p>
              <p className="text-sm text-secondary-text">Manage your API access tokens</p>
            </div>
          </div>
          <Button variant="secondary">Manage</Button>
        </div>
      </div>

      <div className="pt-6 border-t border-border">
        <h4 className="font-medium text-primary-text mb-3">Active Sessions</h4>
        <div className="space-y-2">
          <SessionRow current={true} />
        </div>
      </div>
    </div>
  )
}

function SessionRow({ current }: { current: boolean }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
      <div className="flex items-center gap-3">
        <Monitor className="w-5 h-5 text-secondary-text" />
        <div>
          <p className="font-medium text-primary-text">Current Session</p>
          <p className="text-sm text-secondary-text">Chrome on Windows • Active now</p>
        </div>
      </div>
      {current && <Badge variant="success" className="text-xs">Current</Badge>}
    </div>
  )
}

function AppearanceTab({ formData, setFormData }: any) {
  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-secondary-text mb-3">Theme</label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {THEMES.map((theme) => (
            <button
              key={theme.value}
              onClick={() => setFormData(prev => ({ ...prev, theme: theme.value }))}
              className={cn(
                'relative p-4 rounded-xl border-2 transition-all duration-200 flex flex-col items-center gap-2',
                formData.theme === theme.value
                  ? 'border-accent bg-accent/10'
                  : 'border-border hover:border-border-hover'
              )}
            >
              <div className="w-12 h-12 rounded-xl bg-surface flex items-center justify-center">
                {theme.icon}
              </div>
              <span className="font-medium text-primary-text">{theme.label}</span>
              {formData.theme === theme.value && (
                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-accent flex items-center justify-center">
                  <CheckCircle className="w-3 h-3 text-background" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="pt-6 border-t border-border">
        <h4 className="font-medium text-primary-text mb-3">Color Accent</h4>
        <div className="flex items-center gap-3">
          <input
            type="color"
            defaultValue="#A8FF60"
            className="w-12 h-12 rounded-xl border border-border cursor-pointer"
          />
          <div>
            <p className="font-medium text-primary-text">Custom Accent Color</p>
            <p className="text-sm text-secondary-text">Choose a custom accent color for the interface</p>
          </div>
        </div>
      </div>
    </div>
  )
}



