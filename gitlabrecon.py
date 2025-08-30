#!/usr/bin/env python3
"""
GitLab Reconnaissance Module for RascalRunner

This module provides reconnaissance capabilities for GitLab repositories,
allowing red teamers to gather intelligence about projects, pipelines, secrets,
and potential attack vectors before launching malicious workflows.

Features:
- Token validation and scope analysis
- Project discovery and enumeration
- Pipeline and job analysis
- Secret and variable detection
- Permission assessment
- Runner identification
- Vulnerability detection

Author: RascalRunner Team
Version: 1.0.0
"""

import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from gitlab_wrapper import GitLabWrapper
from rich.console import Console
from rich.table import Table
from rich import print as rprint


class GitLabRecon:
    """GitLab reconnaissance class for gathering intelligence."""
    
    def __init__(self, token: str, base_url: str = "https://gitlab.com"):
        """
        Initialize GitLab reconnaissance.
        
        Args:
            token: GitLab personal access token
            base_url: GitLab instance base URL
        """
        self.wrapper = GitLabWrapper(token, base_url)
        self.console = Console()
        self.token_info = {}
        self.projects = []
        self.targets = []
    
    def run_reconnaissance(self) -> Dict[str, Any]:
        """Run comprehensive reconnaissance and return results."""
        self.console.print("\n[bold blue]🔍 Starting GitLab Reconnaissance[/bold blue]\n")
        
        # Test connection
        if not self.wrapper.test_connection():
            self.console.print("[bold red]❌ Connection failed. Check token and URL.[/bold red]")
            return {}
        
        # Gather intelligence
        self.gather_token_info()
        self.discover_projects()
        self.analyze_targets()
        
        # Display results
        self.display_token_info()
        self.display_target_analysis()
        
        return self.generate_report()
    
    def gather_token_info(self):
        """Gather information about the access token."""
        try:
            user_info = self.wrapper.get_user_info()
            self.token_info = {
                "username": user_info.get("username"),
                "name": user_info.get("name"),
                "email": user_info.get("email"),
                "id": user_info.get("id"),
                "is_admin": user_info.get("is_admin", False),
                "can_create_group": user_info.get("can_create_group", False),
                "can_create_project": user_info.get("can_create_project", False),
                "two_factor_enabled": user_info.get("two_factor_enabled", False),
                "external": user_info.get("external", False)
            }
        except Exception as e:
            self.console.print(f"[red]Error gathering token info: {e}[/red]")
    
    def discover_projects(self):
        """Discover accessible projects."""
        try:
            self.projects = self.wrapper.list_projects(owned=True)
            # Also try to get projects where user has access but doesn't own
            try:
                member_projects = self.wrapper.list_projects(owned=False)
                self.projects.extend(member_projects)
            except:
                pass
        except Exception as e:
            self.console.print(f"[red]Error discovering projects: {e}[/red]")
    
    def analyze_targets(self):
        """Analyze projects for potential targets."""
        for project in self.projects:
            try:
                target_info = self.analyze_project(project)
                if target_info:
                    self.targets.append(target_info)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to analyze project {project.get('name', 'unknown')}: {e}[/yellow]")
    
    def analyze_project(self, project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single project for intelligence."""
        project_id = project.get("id")
        if not project_id:
            return None
        
        # Basic project info
        target = {
            "id": project_id,
            "name": project.get("name"),
            "path_with_namespace": project.get("path_with_namespace"),
            "visibility": project.get("visibility"),
            "permissions": project.get("permissions", {}),
            "has_ci": bool(project.get(".gitlab-ci.yml")),
            "runners_enabled": project.get("runners_enabled", False),
            "issues_enabled": project.get("issues_enabled", False),
            "merge_requests_enabled": project.get("merge_requests_enabled", False),
            "pipelines": [],
            "variables": [],
            "runners": []
        }
        
        # TODO: Implement detailed analysis
        # - Get CI/CD pipelines
        # - List project variables
        # - Enumerate runners
        # - Check for secrets in code
        # - Analyze pipeline configurations
        
        return target
    
    def display_token_info(self):
        """Display token information in a formatted table."""
        table = Table(title="🔑 Token Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in self.token_info.items():
            if value is not None:
                display_value = "✅ Yes" if value is True else "❌ No" if value is False else str(value)
                table.add_row(key.replace("_", " ").title(), display_value)
        
        self.console.print(table)
        self.console.print()
    
    def display_target_analysis(self):
        """Display target analysis in a formatted table."""
        if not self.targets:
            self.console.print("[yellow]No suitable targets found.[/yellow]")
            return
        
        table = Table(title="🎯 Target Analysis")
        table.add_column("Project", style="cyan")
        table.add_column("Visibility", style="white")
        table.add_column("Permissions", style="green")
        table.add_column("CI/CD", style="yellow")
        table.add_column("Runners", style="magenta")
        
        for target in self.targets:
            permissions = target.get("permissions", {})
            access_level = "Unknown"
            if permissions:
                # Determine access level based on permissions
                if permissions.get("project_access", {}).get("access_level") >= 40:
                    access_level = "Maintainer+"
                elif permissions.get("project_access", {}).get("access_level") >= 30:
                    access_level = "Developer"
                elif permissions.get("project_access", {}).get("access_level") >= 20:
                    access_level = "Reporter"
                else:
                    access_level = "Guest"
            
            ci_status = "✅ Enabled" if target.get("has_ci") else "❌ Disabled"
            runners_status = "✅ Enabled" if target.get("runners_enabled") else "❌ Disabled"
            
            table.add_row(
                target.get("path_with_namespace", "Unknown"),
                target.get("visibility", "Unknown").title(),
                access_level,
                ci_status,
                runners_status
            )
        
        self.console.print(table)
        self.console.print()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "token_info": self.token_info,
            "total_projects": len(self.projects),
            "suitable_targets": len(self.targets),
            "targets": self.targets
        }
    
    def save_report(self, filename: str):
        """Save reconnaissance report to file."""
        report = self.generate_report()
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            self.console.print(f"[green]Report saved to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error saving report: {e}[/red]")


def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitLab Reconnaissance Tool")
    parser.add_argument("--token", "-t", required=True, help="GitLab access token")
    parser.add_argument("--url", "-u", default="https://gitlab.com", help="GitLab instance URL")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    recon = GitLabRecon(args.token, args.url)
    report = recon.run_reconnaissance()
    
    if args.output:
        recon.save_report(args.output)
    
    return report


if __name__ == "__main__":
    main()
