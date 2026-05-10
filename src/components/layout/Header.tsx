"use client";

import { Bell, Search } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { logoutAction } from "@/actions/auth";

export function Header({ user }: { user?: { email: string, department: string } }) {
  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex-1 flex items-center">
      </div>
      
      <div className="flex items-center gap-4">
        
        <DropdownMenu>
          <DropdownMenuTrigger className="relative h-8 w-8 rounded-full focus:outline-none ring-0">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary text-primary-foreground">FS</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end">
            <div className="px-2 py-1.5 font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none uppercase">{user?.department || 'Department'}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email || 'faculty@university.edu'}
                </p>
              </div>
            </div>
            <DropdownMenuSeparator />
            <form action={logoutAction}>
              <button type="submit" className="w-full text-left">
                <DropdownMenuItem>
                  Log out
                </DropdownMenuItem>
              </button>
            </form>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
