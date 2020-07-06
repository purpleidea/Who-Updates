## Live Dashboard for Checking Versions of Common Desktop Linux Software Across Snap, Flatpak, Apt

#### Link: https://fortwire.github.io/Who-Updates

#### Setup:

	getVersion.py - Retrieve the latest software versions
	commit.sh - Commit them to github repo
	main.sh - Wrapper for the two scripts above. Used in cronjob for every 6 hours to be run.
	index.md - The output from the script
	list.json - List of applications to check software versions
	
	# crontab -e
	0 */6 * * * /root/Who-Updates/main.sh >/dev/null 2>&1
	
#### Request:

To add software send request in github
