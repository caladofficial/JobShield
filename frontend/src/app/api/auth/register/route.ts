import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password, full_name } = body

    if (!email || !password) {
      return NextResponse.json({ detail: 'Email and password are required' }, { status: 400 })
    }

    // In demo mode, we just return success
    // In production, this would create a user in the database
    return NextResponse.json({ message: 'Registration successful' }, { status: 201 })
  } catch (error) {
    return NextResponse.json({ detail: 'Registration failed' }, { status: 500 })
  }
}