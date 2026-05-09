"use server";

import { cookies } from "next/headers";

export async function uploadCSVAction(formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    return { error: "Unauthorized" };
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/api/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      return { error: "Upload failed" };
    }
    
    return { success: true };
  } catch (error) {
    console.error("Upload error:", error);
    return { error: "Failed to connect to backend" };
  }
}
