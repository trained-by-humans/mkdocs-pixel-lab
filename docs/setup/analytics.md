# Analytics and privacy

Analytics is off by default. Pixel Lab includes an optional Google Analytics 4
integration with an opt-in consent prompt. This documentation website does
not enable analytics.

## Enable GA4

Configure the integration under `extra.analytics`:

```yaml
site_url: https://example.com/docs/
extra:
  analytics:
    provider: google
    measurement_id: G-XXXXXXXXXX
    privacy_policy: https://example.com/privacy/
```

> [!CAUTION]
>
> Use your Web data stream's GA4 Measurement ID, not a Firebase API key or
> Tag Manager ID.

| Parameter | Default | Effect |
| --- | --- | --- |
| `provider` | Not set | Selects the integration; only `google` is supported |
| `measurement_id` | Not set | Selects the GA4 Web data stream using its `G-…` ID |
| `privacy_policy` | Not set | Adds the policy link to the prompt and footer; required for analytics |
| `enabled` | `true` within a configured integration | `false` disables analytics while retaining a configured policy link |

MkDocs' top-level `site_url` supplies your production address:

| Parameter | Default | Effect |
| --- | --- | --- |
| `site_url` | Not set | Defines the production URL used to guard collection; local and alternate-host previews don't collect visits |

Missing or invalid integration settings leave analytics off.

The prompt appears on HTTPS visits matching `site_url`. Local development
and alternate-host previews don't collect visits. Allow analytics loads the
Google tag; Decline doesn't. The Analytics settings link in the footer lets readers
change their choice. Withdrawal attempts to remove the site's GA cookies and
reloads the page. If browser storage is blocked, consent lasts only for the
current page.

## Privacy link

The `privacy_policy` link appears in the prompt and footer. Relative paths
such as `privacy/` also work from nested pages. Keeping the URL while setting
`enabled: false` preserves the footer policy link.

Publish a notice appropriate to your organization and data practices. The
consent prompt isn't a certification of legal compliance.

## Shared consent

By default, consent is scoped to each site URL and Measurement ID. To share
acceptance and rejection across a domain and its subdomains, use the same
Measurement ID and `consent_domain` on every participating site:

```yaml hl_lines="6"
extra:
  analytics:
    provider: google
    measurement_id: G-XXXXXXXXXX
    privacy_policy: https://example.com/privacy/
    consent_domain: example.com
```

| Parameter | Default | Effect |
| --- | --- | --- |
| `consent_domain` | Not set | Shares consent across the specified domain and its subdomains instead of keeping site-specific consent |

Use this only for sites you control under one privacy policy, never shared
hosts such as `github.io`. A consent-only cookie uses `Secure`, `SameSite=Lax`,
`Path=/`, and a 180-day lifetime. GA cookies remain hostname-specific. Invalid
domains disable analytics, and changing consent scope requires a new choice.

## Verify production behavior

1. Create a GA4 property and Web stream for the production site.
2. Disable history-based page changes in Enhanced measurement's page-view
   settings: heading fragments aren't separate visits.
3. Review other automatic measurements and avoid sending personal information
   in page titles or events.
4. Verify acceptance in GA4 Realtime. In a fresh browser context, decline and
   confirm Google requests are absent.

Advertising consent remains denied, Google Signals and advertising
personalization are disabled, and initial URLs/referrers omit query strings
and fragments. Reports describe consenting visitors, not all visits.

## Further customization

Style the consent prompt with these `theme` settings:

| Parameter | Default | Effect |
| --- | --- | --- |
| `header_background` | Leaf green · `#4caf50` | Allow analytics button background |
| `accent_foreground_color` | Near-black · `#101410` | Allow analytics button text |
| `surface_color` | Ivory · `#fffdf2` | Consent prompt background |
| `surface_alt_color` | Pale khaki · `#e8e4cf` | Decline button background |
| `highlight_color` | Golden yellow · `#f5c842` | Decline button background on hover |
| `border_color` | Near-black · `#101410` | Prompt and button outlines |
| `shadow_color` | Near-black · `#101410` | Prompt's pixel shadow |

See [Common attributes](../reference/configuration.md#common-attributes).
