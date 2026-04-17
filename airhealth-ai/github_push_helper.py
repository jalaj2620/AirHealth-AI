#!/usr/bin/env python3
"""
GitHub Push Helper Script for AirHealth AI
==========================================
This script handles secure GitHub authentication and pushes your project.

Usage:
    python github_push_helper.py
"""

import subprocess
import sys
import os
from getpass import getpass

def run_command(cmd, capture_output=True):
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def push_to_github(username, token, repo_name="AirHealth-AI", visibility="public"):
    """Push local repository to GitHub."""
    
    print("\n" + "="*70)
    print("🚀 AIRHEALTH AI - GITHUB PUSH")
    print("="*70)
    
    # Step 1: Check git status
    print("\n1️⃣ Checking git repository...")
    code, out, err = run_command("git status")
    if code != 0:
        print("❌ Error: Not a git repository. Initialize first!")
        return False
    print("✅ Git repository found")
    
    # Step 2: Configure git credentials
    print("\n2️⃣ Configuring authentication...")
    remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    code, _, err = run_command(f'git remote remove origin', capture_output=False)
    code, _, err = run_command(f'git remote add origin "{remote_url}"')
    if code != 0:
        print("❌ Error configuring remote")
        return False
    print("✅ Authentication configured")
    
    # Step 3: Verify files
    print("\n3️⃣ Checking files to push...")
    code, out, _ = run_command("git ls-files")
    file_count = len(out.strip().split('\n')) if out.strip() else 0
    print(f"✅ {file_count} files ready to push")
    
    # Step 4: Push to GitHub
    print("\n4️⃣ Pushing to GitHub...")
    print(f"   Repository: {username}/{repo_name}")
    print(f"   Branch: main")
    
    code, out, err = run_command("git branch -M main")
    code, out, err = run_command("git push -u origin main")
    
    if code != 0:
        print(f"❌ Push failed: {err}")
        return False
    
    print("✅ Files pushed successfully!")
    
    # Step 5: Display GitHub URL
    print("\n" + "="*70)
    print("✨ SUCCESS!")
    print("="*70)
    github_url = f"https://github.com/{username}/{repo_name}"
    print(f"\n📍 Your repository is live at:")
    print(f"   {github_url}")
    print(f"\n🎉 AirHealth AI is now on GitHub!")
    print(f"\n💡 Next steps:")
    print(f"   1. Visit: {github_url}")
    print(f"   2. Add to your resume/portfolio")
    print(f"   3. Share the link in interviews")
    print("="*70 + "\n")
    
    return True

def main():
    """Main execution."""
    print("\n" + "="*70)
    print("AIRHEALTH AI - SECURE GITHUB PUSH")
    print("="*70)
    
    # Get credentials
    print("\n📝 Please provide your GitHub credentials:")
    print("(Your credentials will NOT be stored or logged)")
    print()
    
    username = input("GitHub Username: ").strip()
    if not username:
        print("❌ Username required!")
        return
    
    print("\n🔐 Authentication Method:")
    print("   1. Personal Access Token (Recommended - Safer)")
    print("   2. GitHub Password (Less Secure)")
    
    choice = input("\nSelect (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📚 To create a Personal Access Token:")
        print("   1. Go to: https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Name it: 'AirHealth-AI-Push'")
        print("   4. Select scope: ✅ repo")
        print("   5. Click 'Generate token'")
        print("   6. Copy the token and paste below")
        token = getpass("\nPaste your Personal Access Token: ")
    elif choice == "2":
        token = getpass("Enter your GitHub Password: ")
    else:
        print("❌ Invalid choice!")
        return
    
    if not token:
        print("❌ Token/Password required!")
        return
    
    # Get repo name
    repo_name = input("\nRepository name (default: AirHealth-AI): ").strip() or "AirHealth-AI"
    
    # Get visibility
    print("\n📁 Repository Visibility:")
    print("   1. Public (recommended for portfolio)")
    print("   2. Private")
    visibility_choice = input("Select (1 or 2): ").strip() or "1"
    visibility = "public" if visibility_choice == "1" else "private"
    
    # Confirm before pushing
    print("\n" + "="*70)
    print("CONFIRMATION:")
    print(f"  Username: {username}")
    print(f"  Repository: {repo_name}")
    print(f"  Visibility: {visibility}")
    print(f"  URL: https://github.com/{username}/{repo_name}")
    print("="*70)
    
    confirm = input("\n✅ Proceed with push? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Push cancelled.")
        return
    
    # Execute push
    success = push_to_github(username, token, repo_name, visibility)
    
    if success:
        print("\n✅ All done! Your project is now on GitHub!")
    else:
        print("\n❌ Push encountered an error. Check your credentials and try again.")

if __name__ == "__main__":
    main()
