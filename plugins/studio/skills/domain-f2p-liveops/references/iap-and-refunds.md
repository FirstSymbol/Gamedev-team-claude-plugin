# IAP plumbing, receipt validation and refunds

## Golden flow (consumables / currency) - grant on server, confirm after grant
1. Client: `PurchaseProduct(productId)` → store UI → `OnPurchasePending(PendingOrder)`.
2. Client → backend: `{store, productId, transactionId, payload}` where payload = Apple
   `Order.Info.Apple.jwsRepresentation` (StoreKit 2) or Google `Order.Info.Receipt`
   (purchase token inside), plus authenticated player id.
3. Backend validates with the store server API (below); checks bundle/package id, product id,
   environment (sandbox only for allow-listed testers), purchase state, not revoked.
4. Backend grants via the economy ledger, idempotent on unique `(store, transactionId)`;
   Google: acknowledge/consume server-side; returns granted bundle + new balances.
5. Client: on backend OK → `ConfirmPurchase(order)` (finishes transaction / consumes).
6. Backend unreachable → do NOT confirm; the pending order is re-delivered on next
   `FetchPurchases()` / launch. Confirming before grant = lost purchases + support tickets.

## Unity IAP v5 (com.unity.purchasing) - verify against the installed version's docs
- Entry `UnityIAPServices.StoreController()`; attach `OnPurchasePending`, `OnPurchaseConfirmed`
  (`ConfirmedOrder` | `FailedOrder`), `OnPurchaseFailed`, `OnProductsFetched`,
  `OnPurchasesFetched` BEFORE `await Connect()`; then `FetchProducts(...)`, `FetchPurchases()`.
- Init requires UGS: `await UnityServices.InitializeAsync()` first.
- `CrossPlatformValidator` local validation removed for StoreKit 2 path in v5; Apple receipt
  validation deprecated → send `jwsRepresentation` to the App Store Server API. StoreKit 1
  fallback (iOS < 15) keeps `Order.Info.Apple.AppReceipt`.
- Versions (Unity docs, 2026): IAP 5.0 → Play Billing 8.0.0 (Unity 2021.3+); 4.15.1 / 5.2+ → 8.3.0;
  5.4 → Play Billing 9.0.0, requires Unity 2022.3+; 5.4+ processes developer data → manage
  consent via `UnityConsent`; `PurchasingController` recommended from 5.5.0. IAP 5.1+ falls back
  to StoreKit 1 below iOS 15 (5.0 had no fallback). Older 4.x with PBL < 8 cannot publish updates.
- Third-party SDKs reading the StoreKit 1 app receipt silently get no iOS data after migration -
  test MMP/analytics revenue events before release.

```csharp
void OnPurchasePending(PendingOrder order) => _ = ValidateAndConfirmAsync(order);

async Task ValidateAndConfirmAsync(PendingOrder order) {
    var info = order.Info;
    var req = new PurchaseClaim(Store: Application.platform == RuntimePlatform.IPhonePlayer ? "apple" : "google",
        Payload: info.Apple?.jwsRepresentation ?? info.Receipt);
    var result = await _backend.ClaimPurchaseAsync(req, destroyCancellationToken); // retries w/ backoff
    if (result.Granted) { _wallet.Apply(result.Balances); _store.ConfirmPurchase(order); }
    // else: leave pending; re-delivered next session. Show "purchase processing" UI, not an error.
}
```

## Apple (StoreKit 2 / App Store Server API)
- Validate: verify the JWS signature chain (x5c → Apple Root CA - G3), then check `bundleId`,
  `productId`, `environment`, `transactionId`, `revocationDate` empty; optionally call
  `GET /inApps/v1/transactions/{transactionId}` for authoritative state.
- Apple ships App Store Server Library for Swift, Java, Python, Node only (no official .NET -
  implement JWS verification with `System.IdentityModel.Tokens.Jwt` + X509 chain check).
- Set `appAccountToken` (UUID per player) on purchase to bind transactions to accounts.
- App Store Server Notifications V2 (signed): `REFUND`, `REVOKE`, `CONSUMPTION_REQUEST`,
  `DID_RENEW`, `EXPIRED`, `DID_FAIL_TO_RENEW`, `GRACE_PERIOD_EXPIRED`... Endpoint must be
  idempotent and verify signatures.
- `CONSUMPTION_REQUEST` (refund asked on any product type): respond via Send Consumption
  Information (`PUT /inApps/v2/transactions/{transactionId}/consumption`; v1 only for Advanced
  Commerce API) within 12 h, only if the customer gave valid consent (`customerConsented`; ATT
  is not consent); if no consent, don't respond. Notifications can arrive out of order - handle
  REFUND without a prior CONSUMPTION_REQUEST.

## Google Play Billing
- Validate with Play Developer API: one-time products `purchases.productsv2.getproductpurchasev2`
  (or legacy `purchases.products.get`), subscriptions `purchases.subscriptionsv2.get`; check
  `purchaseState`, `packageName`, product id, `obfuscatedExternalAccountId` = your player id.
- Acknowledge within 3 days or Google auto-refunds; consumables must be consumed to be
  re-purchasable.
- Real-time developer notifications (Cloud Pub/Sub): one-time, subscription and voided
  purchase notifications; poll Voided Purchases API as a backstop (daily job).
- Play Billing Library: v8+ required for new apps/updates since 2026-08-31 (extension ended
  2026-11-01); v8 supported to 2027-08-31, v9 to 2028-08-31 (Play deprecation FAQ) - target v9.

## Refunds, chargebacks, abuse
| Event | Action |
|---|---|
| Refund/void of consumable currency | ledger clawback entry; balance may go negative (block spend until positive) |
| Refund of durable/non-consumable | revoke entitlement; keep cosmetic progress record for support |
| Subscription refund/revoke | end entitlement immediately; notify in inbox |
| Repeat refunder (e.g. >= 2 in 90 d - set policy) | restrict purchasing / require support contact; no silent ban |
| Fake receipts (jailbreak/patchers) | rejected by server validation; log + rate-limit |
| Receipt replay across accounts | unique `(store, transactionId)` index; bind via appAccountToken / obfuscated id |
- Refund policy text and any account action wording → compliance-advisor (consumer law
  varies: EU/UK withdrawal rights for digital content, Japan, Korea - needs human legal review).
- Track refund rate per SKU/geo/segment; spikes after an event = investigate offer clarity.

## Subscriptions (VIP, pass auto-renew)
- Server is source of truth for entitlement; client caches expiry. Handle grace period,
  billing retry, upgrades/downgrades, family sharing (Apple), resubscribe.
- Show price, period, renewal terms and cancel path before purchase (Apple 3.1.2, Google policy).

## Other platforms
- Steam: microtransactions via Steamworks Web API `ISteamMicroTxn` (InitTxn → user approves in
  overlay → FinalizeTxn) server-side; see `studio:domain-pc-console`.
- Web shops / external purchase links: allowed only under region-specific rules. Apple US
  storefront: buttons/external links allowed (3.1.1(a)/3.1.3, guidelines 2026-10-16); EU DMA,
  Korea, Japan via entitlements; Google: enrolled programs in eligible regions (Payments policy
  s. 8-9) - verify: per-region fees/commission in Apple and Play program terms before launch.

## Testing
- Unity IAP Fake Store in Editor; Apple sandbox testers + StoreKit configuration file in Xcode +
  TestFlight; Google license testers + internal testing track; test refunds in both sandboxes.
- Test matrix: success, cancel, pending (Google slow cards), network loss between steps 2-5,
  app kill after store success, restore on new device, refund notification, duplicate delivery.

## Sources
- Unity: Upgrade to IAP v5: https://docs.unity.com/en-us/iap/upgrade-to-iap-v5
- Unity IAP 5.3 changelog: https://docs.unity3d.com/Packages/com.unity.purchasing@5.3/changelog/CHANGELOG.html
- Apple: Send Consumption Information: https://developer.apple.com/documentation/appstoreserverapi/send-consumption-information.md (v1: .../send-consumption-information-v1.md)
- Apple App Store Server Library (Node; lists Swift, Python, Java): https://github.com/apple/app-store-server-library-node
- Google Play Developer API, purchases.productsv2: https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.productsv2
- Android: Play Billing Library deprecation FAQ: https://developer.android.com/google/play/billing/deprecation-faq
- Google Play Payments policy: https://support.google.com/googleplay/android-developer/answer/9858738
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- RevenueCat: Play Billing 8 migration: https://revenuecat.com/blog/engineering/play-billing-8-migration/
- Foresight Mobile: Play Billing Library 8 deadlines: https://foresightmobile.com/blog/google-play-billing-library-8-migration
