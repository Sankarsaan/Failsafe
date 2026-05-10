"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function loginAction(formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { error: "Missing required fields" };
  }

  let redirectUrl = "/dashboard";
  try {
    const res = await fetch("http://127.0.0.1:8000/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!res.ok) {
      return { error: "Invalid credentials or pending approval" };
    }

    const data = await res.json();
    const token = data.access_token;

    const cookieStore = await cookies();
    cookieStore.set({
      name: "auth_token",
      value: token,
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24, // 1 day
    });

    // Decode token to find role
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    const payload = JSON.parse(jsonPayload);
    
    if (payload.role === "admin") {
      redirectUrl = "/admin/dashboard";
    }
  } catch (error) {
    return { error: "Failed to connect to backend" };
  }
  
  redirect(redirectUrl);
}

export async function registerAction(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const department = formData.get("department") as string;

  if (!name || !email || !password || !department) {
    return { error: "Missing required fields" };
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        email,
        password,
        department,
      }),
    });

    if (!res.ok) {
      return { error: "Registration failed" };
    }

    const data = await res.json();
    return { success: true, message: data.message || "Registration submitted successfully." };

  } catch (error) {
    return { error: "Failed to connect to backend" };
  }
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("auth_token");
  redirect("/login");
}
