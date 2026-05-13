"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { registerAction } from "@/actions/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";

const formSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  email: z.string().email({ message: "Invalid email address." }),
  faculty_id: z.string().min(3, { message: "Faculty ID must be at least 3 characters." }),
  password: z.string().min(6, { message: "Password must be at least 6 characters." }),
  department: z.enum(["cse", "mnc", "dsai", "mechanical", "chemical", "civil", "electrical"], {
    message: "Please select a valid department.",
  }),
});

export default function RegisterPage() {
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      faculty_id: "",
      password: "",
      department: "" as any,
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setErrorMsg(null);
    const formData = new FormData();
    formData.append("name", values.name);
    formData.append("email", values.email);
    formData.append("faculty_id", values.faculty_id);
    formData.append("password", values.password);
    formData.append("department", values.department);
    
    const res = await registerAction(formData);
    if (res && res.error) {
      setErrorMsg(res.error);
    } else if (res && res.success) {
      setSuccessMsg(res.message || "Registration submitted for HOD approval.");
    }
  }

  if (successMsg) {
    return (
      <Card className="w-[450px] shadow-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-green-100 rounded-full">
              <ShieldCheck className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Registration Submitted</CardTitle>
          <CardDescription className="mt-4">{successMsg}</CardDescription>
        </CardHeader>
        <CardFooter className="flex justify-center mt-6">
          <Link href="/login" className="text-primary hover:underline font-medium">
            Return to Sign in
          </Link>
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card className="w-[450px] shadow-lg">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-primary/10 rounded-full">
            <ShieldCheck className="w-8 h-8 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl font-bold tracking-tight">Create an Account</CardTitle>
        <CardDescription>Join FAILSAFE to identify and support at-risk students.</CardDescription>
      </CardHeader>
      <CardContent>
        {errorMsg && <div className="text-red-500 text-sm mb-4 text-center">{errorMsg}</div>}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Full Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Dr. FirstName MiddleName LastName" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="faculty@failsafe.edu" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="faculty_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Faculty ID</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. FAC-CSE-001" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="••••••••" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="department"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Department</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a department" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="cse">Computer Science & Engineering</SelectItem>
                      <SelectItem value="mnc">Mathematics and Computing</SelectItem>
                      <SelectItem value="dsai">Data Science & AI</SelectItem>
                      <SelectItem value="mechanical">Mechanical Engineering</SelectItem>
                      <SelectItem value="chemical">Chemical Engineering</SelectItem>
                      <SelectItem value="civil">Civil Engineering</SelectItem>
                      <SelectItem value="electrical">Electrical Engineering</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full mt-4">Register</Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex justify-center text-sm text-muted-foreground">
        <p>
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
