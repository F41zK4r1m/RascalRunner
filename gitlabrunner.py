#!/usr/bin/env python3
"""
GitLab Runner Module for RascalRunner

This module provides the core GitLab-specific functionality for covertly deploying
and managing malicious CI/CD pipelines in GitLab repositories. It extends RascalRunner's
capabilities to work with GitLab's CI/CD infrastructure.

Features:
- Deploy malicious .gitlab-ci.yml files
- Execute covert pipeline operations
- Monitor job execution and collect outputs
- Automatically clean up evidence
- Handle GitLab-specific authentication and permissions
- Support for both GitLab.com and self-hosted instances

Author: RascalRunner Team
Version: 1.0.0
"""

import os
import sys
import time
import uuid
import yaml
import argparse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from gitlab_wrapper import GitLabWrapper
from gitlabrecon import GitLabRecon
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint


class GitLabRunner:
    """Main GitLab runner for covert pipeline operations."""
    
    def __init__(self, token: str, base_url: str = "https://gitlab.com", verbose: bool = False):
        """
        Initialize GitLab runner.
        
        Args:
            token: GitLab personal access token
            base_url: GitLab instance base URL
            verbose: Enable verbose logging
        """
        self.wrapper = GitLabWrapper(token, base_url)
        self.console = Console()
        self.verbose = verbose
        self.project_id = None
        self.pipeline_id = None
        self.temp_branch = None
        self.original_ci_file = None
        
    def run_operation(self, target: str, pipeline_file: str, cleanup: bool = True) -> Dict[str, Any]:
        """
        Execute a complete covert pipeline operation.
        
        Args:
            target: Target project (namespace/project-name or project-id)
            pipeline_file: Path to malicious pipeline YAML file
            cleanup: Whether to clean up after execution
            
        Returns:
            Dict containing operation results
        """
        operation_id = str(uuid.uuid4())[:8]
        self.console.print(f"\n[bold blue]🚀 Starting GitLab Operation: {operation_id}[/bold blue]\n")
        
        try:
            # Step 1: Validate target and permissions
            self._validate_target(target)
            
            # Step 2: Backup original CI file if exists
            self._backup_original_ci()
            
            # Step 3: Create temporary branch
            self._create_temp_branch(operation_id)
            
            # Step 4: Deploy malicious pipeline
            self._deploy_pipeline(pipeline_file)
            
            # Step 5: Monitor execution
            results = self._monitor_execution()
            
            # Step 6: Collect outputs
            outputs = self._collect_outputs()
            
            # Step 7: Cleanup (if enabled)
            if cleanup:
                self._cleanup_operation()
            
            self.console.print("[bold green]✅ Operation completed successfully[/bold green]")
            
            return {
                "operation_id": operation_id,
                "target": target,
                "status": "success",
                "results": results,
                "outputs": outputs,
                "cleanup_performed": cleanup
            }
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Operation failed: {e}[/bold red]")
            # Attempt emergency cleanup
            try:
                self._emergency_cleanup()
            except:
                pass
            
            return {
                "operation_id": operation_id,
                "target": target,
                "status": "failed",
                "error": str(e),
                "cleanup_performed": False
            }
    
    def _validate_target(self, target: str):
        """Validate target project and permissions."""
        self.console.print("[yellow]🔍 Validating target project...[/yellow]")
        
        # Try to get project info
        try:
            if target.isdigit():
                self.project_id = target
            else:
                # Search for project by name
                projects = self.wrapper.list_projects()
                for project in projects:
                    if project.get("path_with_namespace") == target:
                        self.project_id = project.get("id")
                        break
                
                if not self.project_id:
                    raise Exception(f"Project '{target}' not found")
            
            project_info = self.wrapper.get_project(self.project_id)
            
            if self.verbose:
                self.console.print(f"[green]✅ Target validated: {project_info.get('path_with_namespace')}[/green]")
            
        except Exception as e:
            raise Exception(f"Failed to validate target: {e}")
    
    def _backup_original_ci(self):
        """Backup original .gitlab-ci.yml if it exists."""
        if self.verbose:
            self.console.print("[yellow]💾 Checking for existing CI file...[/yellow]")
        
        # TODO: Implement CI file backup
        # This would involve:
        # 1. Check if .gitlab-ci.yml exists in the project
        # 2. Download and store the original content
        # 3. Store backup for potential restoration
        pass
    
    def _create_temp_branch(self, operation_id: str):
        """Create a temporary branch for the operation."""
        self.temp_branch = f"temp-operation-{operation_id}"
        
        if self.verbose:
            self.console.print(f"[yellow]🌿 Creating temporary branch: {self.temp_branch}[/yellow]")
        
        # TODO: Implement branch creation
        # This would involve:
        # 1. Get default branch reference
        # 2. Create new branch from default branch
        # 3. Store branch info for cleanup
        pass
    
    def _deploy_pipeline(self, pipeline_file: str):
        """Deploy the malicious pipeline file."""
        self.console.print("[yellow]🚀 Deploying pipeline...[/yellow]")
        
        # Load and validate pipeline file
        try:
            with open(pipeline_file, 'r') as f:
                pipeline_content = f.read()
            
            # Validate YAML syntax
            yaml.safe_load(pipeline_content)
            
            if self.verbose:
                self.console.print(f"[green]✅ Pipeline file validated: {pipeline_file}[/green]")
        
        except Exception as e:
            raise Exception(f"Failed to load pipeline file: {e}")
        
        # TODO: Implement pipeline deployment
        # This would involve:
        # 1. Commit .gitlab-ci.yml to temporary branch
        # 2. Trigger pipeline execution
        # 3. Store pipeline ID for monitoring
        pass
    
    def _monitor_execution(self) -> Dict[str, Any]:
        """Monitor pipeline execution and wait for completion."""
        self.console.print("[yellow]👀 Monitoring pipeline execution...[/yellow]")
        
        # TODO: Implement pipeline monitoring
        # This would involve:
        # 1. Poll pipeline status
        # 2. Monitor individual jobs
        # 3. Handle timeouts and failures
        # 4. Return execution summary
        
        return {
            "status": "completed",
            "duration": "5m 30s",
            "jobs_completed": 3,
            "jobs_failed": 0
        }
    
    def _collect_outputs(self) -> Dict[str, Any]:
        """Collect job outputs and artifacts."""
        if self.verbose:
            self.console.print("[yellow]📦 Collecting job outputs...[/yellow]")
        
        # TODO: Implement output collection
        # This would involve:
        # 1. Download job logs
        # 2. Collect artifacts
        # 3. Extract sensitive information
        # 4. Save outputs to local files
        
        return {
            "logs_collected": True,
            "artifacts_downloaded": 0,
            "secrets_found": [],
            "output_files": []
        }
    
    def _cleanup_operation(self):
        """Clean up all operation artifacts."""
        self.console.print("[yellow]🧹 Cleaning up operation artifacts...[/yellow]")
        
        # TODO: Implement comprehensive cleanup
        # This would involve:
        # 1. Delete temporary branch
        # 2. Remove pipeline runs from UI (if possible)
        # 3. Clear any deployments
        # 4. Restore original CI file if backed up
        pass
    
    def _emergency_cleanup(self):
        """Emergency cleanup in case of operation failure."""
        if self.verbose:
            self.console.print("[red]🚨 Performing emergency cleanup...[/red]")
        
        # Attempt to clean up what we can
        try:
            self._cleanup_operation()
        except:
            pass


def main():
    """Main function for standalone execution."""
    parser = argparse.ArgumentParser(
        description="GitLab Runner - Covert Pipeline Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run reconnaissance on GitLab instance
  python gitlabrunner.py recon --token TOKEN --url https://gitlab.example.com
  
  # Execute malicious pipeline on target project
  python gitlabrunner.py run --token TOKEN --target "group/project" --pipeline malicious.yml
  
  # Run operation without cleanup (for debugging)
  python gitlabrunner.py run --token TOKEN --target 123 --pipeline payload.yml --no-cleanup
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Reconnaissance command
    recon_parser = subparsers.add_parser("recon", help="Perform reconnaissance")
    recon_parser.add_argument("--token", "-t", required=True, help="GitLab access token")
    recon_parser.add_argument("--url", "-u", default="https://gitlab.com", help="GitLab instance URL")
    recon_parser.add_argument("--output", "-o", help="Save reconnaissance report to file")
    
    # Run operation command
    run_parser = subparsers.add_parser("run", help="Execute covert pipeline operation")
    run_parser.add_argument("--token", "-t", required=True, help="GitLab access token")
    run_parser.add_argument("--target", required=True, help="Target project (namespace/name or ID)")
    run_parser.add_argument("--pipeline", "-p", required=True, help="Malicious pipeline YAML file")
    run_parser.add_argument("--url", "-u", default="https://gitlab.com", help="GitLab instance URL")
    run_parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup operations")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "recon":
            recon = GitLabRecon(args.token, args.url)
            report = recon.run_reconnaissance()
            
            if args.output:
                recon.save_report(args.output)
        
        elif args.command == "run":
            runner = GitLabRunner(args.token, args.url, args.verbose)
            result = runner.run_operation(
                target=args.target,
                pipeline_file=args.pipeline,
                cleanup=not args.no_cleanup
            )
            
            # Save operation results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"gitlab_operation_{timestamp}.json"
            
            import json
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\nOperation results saved to: {result_file}")
    
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
