# US-<NNN>: <short verb-object title>
Status: draft | ready | in progress | done   Priority: <Must/Should/Could> (RICE <score>)
Release slice: <walking skeleton | R1 | R2>   Epic/activity: <story-map activity>
Traces: goal <G-n> · rules <BR-n, BR-m> · GDD <link/section> · NFR <NFR-n>

## Story
As a <role/persona>, I want <capability>, so that <benefit tied to goal>.

## Context / notes
- <why now, data or evidence, links to elicitation notes>
- Out of scope: <explicit exclusions>

## Acceptance criteria
```gherkin
Feature: <feature name>
  Rule: <BR-n text>
  Scenario: <happy path>
    Given <state>
    When <single action>
    Then <observable outcome>
  Scenario: <error/negative path>
    Given <state>
    When <action>
    Then <outcome incl. message/code>
  Scenario: <boundary / duplicate / offline>
    Given <state>
    When <action>
    Then <outcome>
```

## Non-functional
- <metric + threshold + condition, or "inherits NFR-n">

## Analytics / ops
- Events: <event_name (properties)> · Admin/CS needs: <tooling, audit> · Config: <remote keys>

## Dependencies & open questions
- <dependency → owner>  · Q: <question → owner, due YYYY-MM-DD>

## INVEST check
- [ ] Independent [ ] Negotiable [ ] Valuable [ ] Estimable [ ] Small (≤ 1 sprint) [ ] Testable
