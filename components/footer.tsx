"use client"

import { Github } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Footer() {
  return (
    <footer className="border-t border-border bg-card mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">
              Feito por{" "}
              <a
                href="https://www.linkedin.com/in/dev-jonathan/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-foreground font-medium hover:underline"
              >
                dev-jonathan
              </a>
            </p>
          </div>

          <Button
            variant="outline"
            size="icon"
            asChild
          >
            <a
              href="https://github.com/dev-jonathan/simple-search-rank"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub Repository"
            >
              <Github className="h-5 w-5" />
            </a>
          </Button>
        </div>
      </div>
    </footer>
  )
}

