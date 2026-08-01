<#
.SYNOPSIS
Fixed git sync workflow for GEO-Industry-Engine.

.DESCRIPTION
Keeps Git writes in PowerShell instead of inside the Codex sandbox. The
script is safe to run from any directory; it resolves the repo root from
the script location.

Actions:
  pull   - fetch origin, verify a clean tree, fast-forward only
  commit - require an explicit path list, stage it, check the staged diff,
           ask for manual confirmation, then commit
  push   - push the current branch to origin with -u
  status - show branch, upstream, short status, and diff stats

Protected branches (master/main) are read-only for this script: commit and
push are rejected. Create an agent/* task branch first.

.PARAMETER Action
One of: pull, commit, push, status.

.PARAMETER Paths
Required for commit. Explicit files/directories to stage. Automatic
staging (git add ., git add -A, git add -u) is disabled.

.PARAMETER Message
Commit message. Use either Message or MessageFile.

.PARAMETER MessageFile
Path to a file containing the commit message. Prefer a file outside the
repository, for example $env:TEMP\geo-commit-message.txt. An in-repo file
triggers a warning and must not appear in -Paths.

.PARAMETER Push
With commit: push after a successful commit.

.EXAMPLE
.\scripts\sync.ps1 pull

.EXAMPLE
git switch master
.\scripts\sync.ps1 pull
git switch -c agent/c55-universe-home

.EXAMPLE
.\scripts\sync.ps1 commit -Paths backend/app/api/v1/universe.py,frontend/src/types/universe.ts -Message "fix: universe sync"

.EXAMPLE
$commitMsg = Join-Path $env:TEMP 'geo-commit-message.txt'
Set-Content -LiteralPath $commitMsg -Value 'fix: universe sync'
.\scripts\sync.ps1 commit -Paths backend/app/api/v1/universe.py -MessageFile $commitMsg

.EXAMPLE
.\scripts\sync.ps1 push
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('pull', 'commit', 'push', 'status')]
    [string]$Action,

    [string[]]$Paths = @(),

    [string]$Message,

    [string]$MessageFile,

    [switch]$Push
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Git = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $Git) {
    throw 'git was not found on PATH. Install Git for Windows and retry.'
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$GitArgs
    )

    $display = ($GitArgs | ForEach-Object {
            if ($_ -match '\s') { "'" + $_ + "'" } else { $_ }
        }) -join ' '
    Write-Host "> git $display" -ForegroundColor DarkGray
    & $Git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs[0]) failed with exit code $LASTEXITCODE"
    }
}

function Get-CurrentBranch {
    $branch = & $Git branch --show-current
    if ($LASTEXITCODE -ne 0 -or -not $branch) {
        throw 'Not on a branch (detached HEAD or no commits). Check out a branch first.'
    }
    return $branch
}

function Assert-CleanTree {
    $changed = @(& $Git status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw 'git status failed.'
    }
    if ($changed.Count -gt 0) {
        Write-Host 'Working tree is not clean. Pull aborted:' -ForegroundColor Yellow
        & $Git status --short --branch
        throw 'Commit or stash local changes before pulling.'
    }
}

function Invoke-Pull {
    $branch = Get-CurrentBranch
    Assert-CleanTree

    $upstream = & $Git rev-parse --verify --quiet --abbrev-ref --symbolic-full-name '@{u}'
    if ($LASTEXITCODE -ne 0) {
        throw "Branch '$branch' has no upstream. Sync master first, then create the task branch; or push this branch first to establish upstream."
    }

    Invoke-Git @('fetch', 'origin')
    Write-Host "Current branch: $branch" -ForegroundColor Cyan
    & $Git status --short --branch

    Invoke-Git @('pull', '--ff-only')

    & $Git status --short --branch
    Write-Host 'Ready: up to date and clean.' -ForegroundColor Green
}

function Invoke-Commit {
    $branch = Get-CurrentBranch
    if ($branch -in @('master', 'main')) {
        throw "Direct commit to protected branch '$branch' is forbidden. Create an agent/* task branch first."
    }

    if ($Message -and $MessageFile) {
        throw 'Use either -Message or -MessageFile, not both.'
    }
    if (-not $Message -and -not $MessageFile) {
        throw 'commit requires -Message or -MessageFile.'
    }

    $normalizedPaths = @()
    foreach ($path in $Paths) {
        foreach ($part in ($path -split ',')) {
            $part = $part.Trim()
            if ($part.Length -gt 0) {
                $normalizedPaths += $part
            }
        }
    }
    $Paths = $normalizedPaths

    if ($Paths.Count -eq 0) {
        throw 'commit requires an explicit -Paths list. Automatic staging is disabled.'
    }

    & $Git diff --cached --quiet
    if ($LASTEXITCODE -eq 1) {
        throw 'Staged changes already exist. Review and unstage them first: git reset.'
    }
    if ($LASTEXITCODE -gt 1) {
        throw 'git diff --cached failed.'
    }

    $messagePath = $null
    if ($MessageFile) {
        if ([System.IO.Path]::IsPathRooted($MessageFile)) {
            $messagePath = $MessageFile
        }
        else {
            $messagePath = Join-Path $RepoRoot $MessageFile
        }
        if (-not (Test-Path -LiteralPath $messagePath -PathType Leaf)) {
            throw "Message file not found or not a regular file: $MessageFile"
        }

        $messageFull = [System.IO.Path]::GetFullPath($messagePath)
        $repoRootFull = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
        if ($messageFull.StartsWith($repoRootFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
            Write-Host "Warning: message file is inside the repository: $messagePath. Prefer $env:TEMP\geo-commit-message.txt." -ForegroundColor Yellow
        }

        foreach ($path in $Paths) {
            $pathFull = if ([System.IO.Path]::IsPathRooted($path)) {
                [System.IO.Path]::GetFullPath($path)
            }
            else {
                [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $path))
            }
            if ([string]::Equals($pathFull, $messageFull, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Message file '$MessageFile' must not be included in -Paths."
            }
        }
    }

    Invoke-Git (@('add', '--') + $Paths)

    Invoke-Git @('diff', '--cached', '--check')
    Invoke-Git @('diff', '--cached', '--stat')
    Invoke-Git @('diff', '--cached', '--name-status')

    $confirmation = Read-Host 'Commit exactly these staged changes? Type YES to continue'
    if ($confirmation -cne 'YES') {
        throw 'Commit cancelled. Staged changes were preserved for review.'
    }

    if ($messagePath) {
        Invoke-Git @('commit', '-F', $messagePath)
    }
    else {
        Invoke-Git @('commit', '-m', $Message)
    }

    & $Git status --short --branch
    Write-Host 'Committed.' -ForegroundColor Green

    if ($Push) {
        Invoke-Push
    }
}

function Invoke-Push {
    $branch = Get-CurrentBranch
    if ($branch -in @('master', 'main')) {
        throw "Direct push to protected branch '$branch' is forbidden. Create an agent/* task branch first."
    }

    Invoke-Git @('push', '-u', 'origin', $branch)

    & $Git status --short --branch
    $shortHead = & $Git rev-parse --short HEAD
    Write-Host "Pushed $shortHead to origin/$branch." -ForegroundColor Green
}

function Show-Status {
    $branch = Get-CurrentBranch

    $upstream = & $Git rev-parse --verify --quiet --abbrev-ref --symbolic-full-name '@{u}'
    if ($LASTEXITCODE -ne 0) {
        $upstream = '(none)'
    }

    Write-Host "Branch:   $branch"
    Write-Host "Upstream: $upstream"
    Write-Host ''
    & $Git status --short --branch
    Write-Host ''
    Write-Host 'Unstaged changes:'
    Invoke-Git @('diff', '--stat')
    Write-Host 'Staged changes:'
    Invoke-Git @('diff', '--cached', '--stat')

    $shortHead = & $Git rev-parse --short HEAD
    $headSubject = & $Git log -1 --pretty=%s
    Write-Host "Last commit: $shortHead $headSubject"
}

Push-Location $RepoRoot
try {
    switch ($Action) {
        'pull' { Invoke-Pull }
        'commit' { Invoke-Commit }
        'push' { Invoke-Push }
        'status' { Show-Status }
    }
}
finally {
    Pop-Location
}
