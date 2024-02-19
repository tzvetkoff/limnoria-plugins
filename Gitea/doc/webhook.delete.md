# "delete" webhook

Sent when a branch or tag is deleted.

``` js
{
  "ref": "foobar",
  "ref_type": "branch",
  "pusher_type": "user",
  "repository__id": 37171,
  "repository__owner__id": 517276,
  "repository__owner__login": "tzvetkoff",
  "repository__owner__login_name": "",
  "repository__owner__full_name": "",
  "repository__owner__email": "tzvetkoff@noreply.try.gitea.io",
  "repository__owner__avatar_url": "https://try.gitea.io/avatar/60ec3d3339146b13659ba48baea599b7",
  "repository__owner__language": "",
  "repository__owner__is_admin": false,
  "repository__owner__last_login": "0001-01-01T00:00:00Z",
  "repository__owner__created": "2022-09-19T02:38:06Z",
  "repository__owner__restricted": false,
  "repository__owner__active": false,
  "repository__owner__prohibit_login": false,
  "repository__owner__location": "",
  "repository__owner__website": "",
  "repository__owner__description": "",
  "repository__owner__visibility": "public",
  "repository__owner__followers_count": 0,
  "repository__owner__following_count": 0,
  "repository__owner__starred_repos_count": 0,
  "repository__owner__username": "tzvetkoff",
  "repository__name": "blah",
  "repository__full_name": "tzvetkoff/blah",
  "repository__description": "",
  "repository__empty": false,
  "repository__private": false,
  "repository__fork": false,
  "repository__template": false,
  "repository__parent": null,
  "repository__mirror": false,
  "repository__size": 93,
  "repository__language": "",
  "repository__languages_url": "https://try.gitea.io/api/v1/repos/tzvetkoff/blah/languages",
  "repository__html_url": "https://try.gitea.io/tzvetkoff/blah",
  "repository__ssh_url": "git@try.gitea.io:tzvetkoff/blah.git",
  "repository__clone_url": "https://try.gitea.io/tzvetkoff/blah.git",
  "repository__original_url": "",
  "repository__website": "",
  "repository__stars_count": 0,
  "repository__forks_count": 1,
  "repository__watchers_count": 1,
  "repository__open_issues_count": 0,
  "repository__open_pr_counter": 0,
  "repository__release_counter": 1,
  "repository__default_branch": "master",
  "repository__archived": false,
  "repository__created_at": "2022-09-19T08:07:02Z",
  "repository__updated_at": "2022-09-19T08:40:25Z",
  "repository__permissions__admin": false,
  "repository__permissions__push": false,
  "repository__permissions__pull": false,
  "repository__has_issues": true,
  "repository__internal_tracker__enable_time_tracker": false,
  "repository__internal_tracker__allow_only_contributors_to_track_time": true,
  "repository__internal_tracker__enable_issue_dependencies": true,
  "repository__has_wiki": true,
  "repository__has_pull_requests": true,
  "repository__has_projects": true,
  "repository__ignore_whitespace_conflicts": false,
  "repository__allow_merge_commits": true,
  "repository__allow_rebase": true,
  "repository__allow_rebase_explicit": true,
  "repository__allow_squash_merge": true,
  "repository__allow_rebase_update": true,
  "repository__default_delete_branch_after_merge": false,
  "repository__default_merge_style": "merge",
  "repository__avatar_url": "",
  "repository__internal": false,
  "repository__mirror_interval": "",
  "repository__mirror_updated": "0001-01-01T00:00:00Z",
  "repository__repo_transfer": null,
  "sender__id": 517276,
  "sender__login": "tzvetkoff",
  "sender__login_name": "",
  "sender__full_name": "",
  "sender__email": "tzvetkoff@noreply.try.gitea.io",
  "sender__avatar_url": "https://try.gitea.io/avatar/60ec3d3339146b13659ba48baea599b7",
  "sender__language": "",
  "sender__is_admin": false,
  "sender__last_login": "0001-01-01T00:00:00Z",
  "sender__created": "2022-09-19T02:38:06Z",
  "sender__restricted": false,
  "sender__active": false,
  "sender__prohibit_login": false,
  "sender__location": "",
  "sender__website": "",
  "sender__description": "",
  "sender__visibility": "public",
  "sender__followers_count": 0,
  "sender__following_count": 0,
  "sender__starred_repos_count": 0,
  "sender__username": "tzvetkoff"
}
```