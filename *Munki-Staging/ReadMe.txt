To understand the workings of Munki-Staging please visit the original:
https://github.com/ox-it/munki-staging

MunkiStagingExecute must be executable. Save this to anywhere on your computer. We recommend your script folder for MunkiRepo

In terminal:
chmod +x PathToMunkiStagingExecute


In order for AutoPkgr to trigger MunkiStaging on Trello you must edit the AutoPkgr application. The best line to do is by adding to link 1578.
Edit AutoPkgr Application

Open /Library/AutoPkg/autopkg with a text editor
Line 1571-1578; 1578 is the one you put subprocess.call
Below is what lines 1571-1578 look like.

# save report plist with the summary data
    if options.report_plist:
        results_report['failures'] = failures
        results_report['summary_results'] = summary_results
        write_plist_exit_on_fail(results_report, options.report_plist)
        log("\nReport plist saved to %s." % options.report_plist)
       import subprocess    subprocess.call(['/PathToMunkiStagingExecute'])
