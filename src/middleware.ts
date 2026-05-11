import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

function decodeJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;

  // Paths that do not require authentication
  const isAuthRoute = request.nextUrl.pathname.startsWith('/login') || 
                      request.nextUrl.pathname.startsWith('/register');

  // Admin paths
  const isAdminRoute = request.nextUrl.pathname.startsWith('/admin');

  // If user is trying to access a protected route without a token
  if (!token && !isAuthRoute) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If user is already authenticated and tries to access login/register, redirect to dashboard
  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Role-based access for admin routes
  if (token && isAdminRoute) {
    const payload = decodeJwt(token);
    if (!payload || payload.role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  // Default redirect root to login
  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
