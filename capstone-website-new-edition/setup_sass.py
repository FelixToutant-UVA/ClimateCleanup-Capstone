"""
SCSS Setup Script for Flask Project
-----------------------------------
This script sets up a SCSS directory structure and converts existing CSS files to SCSS.
It creates a well-organized SCSS architecture following the 7-1 pattern (simplified).
"""

import os
import re
import shutil
import subprocess
import sys

# Define the directory structure
SCSS_DIR = os.path.join('website', 'static', 'scss')
CSS_DIR = os.path.join('website', 'static', 'css')
CSS_OUTPUT_DIR = CSS_DIR  # Where compiled CSS will go

# Define the SCSS architecture
SCSS_STRUCTURE = {
    'abstracts': {
        '_variables.scss': '// Variables: colors, fonts, sizes, etc.\n\n// Colors\n$color-primary: #2e7d32;\n$color-primary-dark: #1b5e20;\n$color-primary-light: #4caf50;\n$color-secondary: #333;\n$color-text: #333;\n$color-text-light: #666;\n$color-background: #fff;\n$color-background-light: #f9f9f9;\n$color-border: #ddd;\n\n// Spacing\n$spacing-xs: 0.25rem;\n$spacing-sm: 0.5rem;\n$spacing-md: 1rem;\n$spacing-lg: 1.5rem;\n$spacing-xl: 2rem;\n$spacing-xxl: 3rem;\n\n// Font sizes\n$font-size-xs: 0.85rem;\n$font-size-sm: 0.9rem;\n$font-size-md: 1rem;\n$font-size-lg: 1.2rem;\n$font-size-xl: 1.5rem;\n$font-size-xxl: 2rem;\n$font-size-hero: 3rem;\n\n// Breakpoints\n$breakpoint-sm: 480px;\n$breakpoint-md: 768px;\n$breakpoint-lg: 992px;\n$breakpoint-xl: 1200px;\n\n// Border radius\n$border-radius-sm: 4px;\n$border-radius-md: 6px;\n$border-radius-lg: 8px;\n$border-radius-xl: 20px;\n\n// Transitions\n$transition-fast: 0.2s;\n$transition-default: 0.3s;\n$transition-slow: 0.5s;\n\n// Box shadows\n$shadow-sm: 0 2px 5px rgba(0, 0, 0, 0.05);\n$shadow-md: 0 3px 10px rgba(0, 0, 0, 0.08);\n$shadow-lg: 0 5px 15px rgba(0, 0, 0, 0.1);\n',
        '_mixins.scss': '// Mixins: reusable style patterns\n\n// Media query mixins\n@mixin respond-to($breakpoint) {\n  @if $breakpoint == sm {\n    @media (max-width: $breakpoint-sm) { @content; }\n  } @else if $breakpoint == md {\n    @media (max-width: $breakpoint-md) { @content; }\n  } @else if $breakpoint == lg {\n    @media (max-width: $breakpoint-lg) { @content; }\n  } @else if $breakpoint == xl {\n    @media (max-width: $breakpoint-xl) { @content; }\n  }\n}\n\n// Flexbox mixins\n@mixin flex-center {\n  display: flex;\n  align-items: center;\n  justify-content: center;\n}\n\n@mixin flex-between {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n}\n\n@mixin flex-column {\n  display: flex;\n  flex-direction: column;\n}\n\n// Button mixins\n@mixin button-base {\n  display: inline-block;\n  padding: $spacing-md $spacing-xl;\n  border-radius: $border-radius-sm;\n  font-weight: 500;\n  text-decoration: none;\n  cursor: pointer;\n  transition: all $transition-default;\n}\n\n@mixin button-primary {\n  @include button-base;\n  background: $color-primary;\n  color: white;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n    box-shadow: $shadow-md;\n  }\n}\n\n@mixin button-secondary {\n  @include button-base;\n  background: transparent;\n  border: 2px solid $color-primary;\n  color: $color-primary;\n  \n  &:hover {\n    background: rgba($color-primary, 0.1);\n  }\n}\n\n// Card mixins\n@mixin card {\n  background: white;\n  border-radius: $border-radius-md;\n  overflow: hidden;\n  box-shadow: $shadow-md;\n  transition: transform $transition-default, box-shadow $transition-default;\n  \n  &:hover {\n    transform: translateY(-5px);\n    box-shadow: $shadow-lg;\n  }\n}\n\n// Form element mixins\n@mixin form-control {\n  width: 100%;\n  padding: $spacing-md;\n  border: 1px solid $color-border;\n  border-radius: $border-radius-sm;\n  font-size: $font-size-md;\n  transition: border-color $transition-default;\n  \n  &:focus {\n    border-color: $color-primary;\n    outline: none;\n  }\n}\n\n// Truncate text with ellipsis\n@mixin text-truncate {\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n\n// Clearfix\n@mixin clearfix {\n  &::after {\n    content: "";\n    display: table;\n    clear: both;\n  }\n}\n',
        '_functions.scss': '// Functions: SCSS functions for calculations\n\n// Convert px to rem\n@function rem($pixels, $context: 16) {\n  @return ($pixels / $context) * 1rem;\n}\n\n// Lighten color by percentage\n@function tint($color, $percentage) {\n  @return mix(white, $color, $percentage);\n}\n\n// Darken color by percentage\n@function shade($color, $percentage) {\n  @return mix(black, $color, $percentage);\n}\n',
    },
    'base': {
        '_reset.scss': '// Reset: CSS reset and base styles\n\n* {\n  margin: 0;\n  padding: 0;\n  box-sizing: border-box;\n}\n\nhtml {\n  font-size: 16px;\n}\n\nbody {\n  font-family: Arial, sans-serif;\n  background: $color-background;\n  color: $color-text;\n  line-height: 1.6;\n}\n\na {\n  text-decoration: none;\n  color: $color-primary;\n  transition: color $transition-default;\n  \n  &:hover {\n    color: $color-primary-dark;\n  }\n}\n\nimg {\n  max-width: 100%;\n  height: auto;\n}\n\nbutton {\n  cursor: pointer;\n}\n',
        '_typography.scss': '// Typography: text styles\n\nh1, h2, h3, h4, h5, h6 {\n  margin-bottom: $spacing-md;\n  font-weight: 500;\n  line-height: 1.2;\n  color: $color-secondary;\n}\n\nh1 {\n  font-size: $font-size-hero;\n}\n\nh2 {\n  font-size: $font-size-xxl;\n}\n\nh3 {\n  font-size: $font-size-xl;\n}\n\nh4 {\n  font-size: $font-size-lg;\n}\n\nh5 {\n  font-size: $font-size-md;\n}\n\nh6 {\n  font-size: $font-size-sm;\n}\n\np {\n  margin-bottom: $spacing-md;\n}\n\n.text-center {\n  text-align: center;\n}\n\n.text-right {\n  text-align: right;\n}\n\n.text-left {\n  text-align: left;\n}\n\n.text-bold {\n  font-weight: bold;\n}\n\n.text-normal {\n  font-weight: normal;\n}\n\n.text-light {\n  font-weight: 300;\n}\n\n.text-primary {\n  color: $color-primary;\n}\n\n.text-secondary {\n  color: $color-secondary;\n}\n\n.text-muted {\n  color: $color-text-light;\n}\n\n.text-white {\n  color: white;\n}\n',
        '_utilities.scss': '// Utilities: helper classes\n\n// Margin utilities\n.mt-1 { margin-top: $spacing-xs; }\n.mt-2 { margin-top: $spacing-sm; }\n.mt-3 { margin-top: $spacing-md; }\n.mt-4 { margin-top: $spacing-lg; }\n.mt-5 { margin-top: $spacing-xl; }\n\n.mb-1 { margin-bottom: $spacing-xs; }\n.mb-2 { margin-bottom: $spacing-sm; }\n.mb-3 { margin-bottom: $spacing-md; }\n.mb-4 { margin-bottom: $spacing-lg; }\n.mb-5 { margin-bottom: $spacing-xl; }\n\n// Display utilities\n.d-flex { display: flex; }\n.d-block { display: block; }\n.d-none { display: none; }\n\n// Flex utilities\n.flex-column { flex-direction: column; }\n.flex-row { flex-direction: row; }\n.flex-wrap { flex-wrap: wrap; }\n.justify-content-center { justify-content: center; }\n.justify-content-between { justify-content: space-between; }\n.align-items-center { align-items: center; }\n\n// Spacing utilities\n.p-1 { padding: $spacing-xs; }\n.p-2 { padding: $spacing-sm; }\n.p-3 { padding: $spacing-md; }\n.p-4 { padding: $spacing-lg; }\n.p-5 { padding: $spacing-xl; }\n\n// Miscellaneous\n.rounded { border-radius: $border-radius-sm; }\n.shadow { box-shadow: $shadow-md; }\n.container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: 0 $spacing-md;\n}\n\n// Responsive utilities\n@include respond-to(md) {\n  .hide-md { display: none; }\n}\n\n@include respond-to(sm) {\n  .hide-sm { display: none; }\n}\n',
    },
    'layout': {
        '_navbar.scss': '// Navbar styles\n\n.navbar {\n  position: sticky;\n  top: 0;\n  z-index: 999;\n  background: $color-primary;\n  color: white;\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  padding: $spacing-md $spacing-xl;\n  box-shadow: $shadow-md;\n  \n  .nav-left {\n    .brand {\n      color: white;\n      text-decoration: none;\n      font-weight: bold;\n      font-size: $font-size-lg;\n      transition: transform $transition-default;\n      \n      &:hover {\n        transform: translateY(-2px);\n      }\n    }\n  }\n  \n  .nav-right {\n    list-style: none;\n    display: flex;\n    gap: $spacing-xl;\n    \n    li {\n      margin: 0;\n      padding: 0;\n    }\n    \n    a {\n      color: white;\n      text-decoration: none;\n      font-weight: 500;\n      position: relative;\n      padding: $spacing-xs 0;\n      transition: color $transition-default;\n      \n      &:not(.signup-btn)::after {\n        content: "";\n        position: absolute;\n        width: 0;\n        height: 2px;\n        bottom: -3px;\n        left: 0;\n        background-color: white;\n        transition: width $transition-default ease;\n        opacity: 0;\n      }\n      \n      &:not(.signup-btn):hover::after {\n        width: 100%;\n        opacity: 1;\n      }\n    }\n    \n    .signup-btn {\n      border: 2px solid white;\n      padding: $spacing-xs $spacing-md;\n      border-radius: $border-radius-xl;\n      background: transparent;\n      color: white;\n      transition: background $transition-default, color $transition-default, transform $transition-fast;\n      \n      &:hover {\n        background: white;\n        color: $color-primary;\n        transform: translateY(-2px);\n      }\n    }\n  }\n  \n  @include respond-to(md) {\n    flex-direction: column;\n    padding: $spacing-md;\n    \n    .nav-left {\n      margin-bottom: $spacing-md;\n    }\n    \n    .nav-right {\n      flex-direction: column;\n      gap: $spacing-md;\n      width: 100%;\n      text-align: center;\n    }\n  }\n}\n',
        '_footer.scss': '// Footer styles\n\nfooter {\n  text-align: center;\n  padding: $spacing-lg;\n  background: $color-primary;\n  color: white;\n  margin-top: $spacing-xl;\n  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);\n  \n  p {\n    margin: 0;\n    font-size: $font-size-sm;\n  }\n}\n\n.custom-fixed-footer {\n  position: fixed;\n  bottom: 0;\n  left: 0;\n  width: 100%;\n  background: transparent;\n  text-align: center;\n  padding: $spacing-sm 0;\n  z-index: 1000;\n  \n  p {\n    margin: 0;\n    font-size: $font-size-sm;\n    color: black;\n  }\n}\n',
        '_grid.scss': '// Grid and layout styles\n\n// Container\n.container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: 0 $spacing-md;\n}\n\n// Simple grid system\n.row {\n  display: flex;\n  flex-wrap: wrap;\n  margin: 0 -$spacing-md;\n}\n\n.col {\n  flex: 1;\n  padding: 0 $spacing-md;\n  min-width: 0;\n}\n\n@for $i from 1 through 12 {\n  .col-#{$i} {\n    flex: 0 0 calc(#{$i} / 12 * 100%);\n    max-width: calc(#{$i} / 12 * 100%);\n    padding: 0 $spacing-md;\n  }\n}\n\n// Responsive columns\n@include respond-to(md) {\n  @for $i from 1 through 12 {\n    .col-md-#{$i} {\n      flex: 0 0 calc(#{$i} / 12 * 100%);\n      max-width: calc(#{$i} / 12 * 100%);\n    }\n  }\n}\n\n@include respond-to(sm) {\n  @for $i from 1 through 12 {\n    .col-sm-#{$i} {\n      flex: 0 0 calc(#{$i} / 12 * 100%);\n      max-width: calc(#{$i} / 12 * 100%);\n    }\n  }\n  \n  .col, [class*="col-"] {\n    flex: 0 0 100%;\n    max-width: 100%;\n  }\n}\n\n// Hero container\n.hero {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  background: #d8f0f0;\n  min-height: 80vh;\n  padding: $spacing-xl;\n  \n  &-left {\n    flex: 1;\n    max-width: 600px;\n    \n    h1 {\n      font-size: $font-size-hero;\n      margin-bottom: $spacing-xl;\n    }\n  }\n  \n  &-right {\n    flex: 1;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    \n    img {\n      max-width: 100%;\n      height: auto;\n      border-radius: $border-radius-sm;\n    }\n  }\n  \n  @include respond-to(md) {\n    flex-direction: column;\n    text-align: center;\n    \n    &-left {\n      margin-bottom: $spacing-xl;\n    }\n  }\n}\n\n// Hero metrics section\n.hero-metrics {\n  position: relative;\n  width: 100%;\n  height: 50vh;\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  overflow: hidden;\n  margin-bottom: $spacing-xl;\n  \n  .hero-image {\n    position: absolute;\n    top: 0;\n    left: 0;\n    width: 100%;\n    height: 100%;\n    z-index: 1;\n    \n    img {\n      width: 100%;\n      height: 100%;\n      object-fit: cover;\n    }\n  }\n  \n  .hero-text {\n    position: relative;\n    z-index: 2;\n    text-align: center;\n    color: white;\n    \n    h1 {\n      font-size: $font-size-xxl;\n      margin-bottom: $spacing-sm;\n    }\n    \n    p {\n      font-size: $font-size-lg;\n    }\n  }\n}\n\n// Metrics grid\n.metrics-grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: $spacing-lg;\n  \n  @include respond-to(md) {\n    grid-template-columns: 1fr;\n  }\n}\n',
    },
    'components': {
        '_buttons.scss': '// Button styles\n\n// Base button styles\n.button-row {\n  display: flex;\n  gap: $spacing-md;\n  \n  @include respond-to(md) {\n    flex-direction: column;\n    align-items: center;\n  }\n}\n\n.cta-button {\n  @include button-base;\n  background: #000;\n  color: white;\n  \n  &:hover {\n    background: #333;\n    transform: translateY(-2px);\n  }\n  \n  &.primary {\n    background: $color-primary;\n    \n    &:hover {\n      background: $color-primary-dark;\n    }\n  }\n  \n  &.secondary {\n    background: transparent;\n    border: 2px solid $color-primary;\n    color: $color-primary;\n    \n    &:hover {\n      background: rgba($color-primary, 0.1);\n    }\n  }\n  \n  @include respond-to(md) {\n    width: 100%;\n    max-width: 250px;\n    text-align: center;\n    margin-bottom: $spacing-sm;\n  }\n}\n\n// Hero button\n.hero-btn {\n  background: $color-primary;\n  color: white;\n  padding: $spacing-md $spacing-xl;\n  border-radius: $border-radius-sm;\n  font-size: $font-size-lg;\n  text-decoration: none;\n  transition: all $transition-default ease;\n  display: inline-block;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n    box-shadow: $shadow-md;\n  }\n}\n\n// Edit button\n.edit-btn {\n  background: $color-primary;\n  color: white;\n  border: none;\n  padding: $spacing-sm $spacing-md;\n  border-radius: $border-radius-sm;\n  font-size: $font-size-sm;\n  cursor: pointer;\n  transition: all $transition-default ease;\n  display: flex;\n  align-items: center;\n  gap: $spacing-sm;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n  }\n}\n\n// Tab button\n.tab-button {\n  background: white;\n  border: 1px solid $color-secondary;\n  color: $color-secondary;\n  padding: $spacing-xs $spacing-sm;\n  cursor: pointer;\n  font-size: $font-size-xs;\n  transition: background $transition-default;\n  \n  &:hover {\n    background: $color-secondary;\n    color: white;\n  }\n  \n  &.active {\n    background: $color-primary;\n    color: white;\n    border-color: $color-primary;\n  }\n}\n',
        '_cards.scss': '// Card styles\n\n// Base card\n.card {\n  @include card;\n  padding: $spacing-lg;\n  \n  h3 {\n    margin-bottom: $spacing-sm;\n  }\n  \n  p {\n    color: $color-text-light;\n    margin-bottom: $spacing-md;\n  }\n}\n\n// Metrics card\n.metrics-card {\n  background: white;\n  border: 1px solid $color-border;\n  padding: $spacing-md;\n  text-align: center;\n  \n  img {\n    max-width: 100%;\n    height: auto;\n    margin-bottom: $spacing-sm;\n  }\n  \n  h3 {\n    margin-bottom: $spacing-xs;\n    font-size: $font-size-lg;\n  }\n  \n  p {\n    font-size: $font-size-sm;\n    color: $color-text-light;\n  }\n}\n\n// Carbon info card\n.carbon-info-card {\n  display: flex;\n  flex-direction: column;\n  align-items: flex-start;\n  text-align: left;\n  \n  a.btn {\n    margin-top: $spacing-sm;\n    text-decoration: none;\n    padding: $spacing-sm $spacing-md;\n    border-radius: $border-radius-sm;\n    font-size: $font-size-sm;\n    font-weight: 500;\n    color: white;\n    background: #007bff;\n    transition: background $transition-default;\n    \n    &:hover {\n      background: #0056b3;\n    }\n  }\n}\n\n// Forest card\n.forest-card {\n  @include card;\n  \n  &-image {\n    position: relative;\n    height: 200px;\n    \n    img {\n      width: 100%;\n      height: 100%;\n      object-fit: cover;\n    }\n  }\n  \n  &-badge {\n    position: absolute;\n    top: $spacing-md;\n    right: $spacing-md;\n    background: rgba(0, 0, 0, 0.6);\n    color: white;\n    padding: $spacing-xs $spacing-sm;\n    border-radius: $border-radius-sm;\n    font-size: $font-size-xs;\n  }\n  \n  &-content {\n    padding: $spacing-lg;\n    \n    h3 {\n      font-size: $font-size-lg;\n      margin-bottom: $spacing-sm;\n      color: $color-secondary;\n    }\n    \n    .forest-location {\n      font-size: $font-size-sm;\n      color: $color-text-light;\n      margin-bottom: $spacing-md;\n    }\n    \n    .forest-description {\n      font-size: $font-size-sm;\n      color: $color-text-light;\n      margin-bottom: $spacing-md;\n      line-height: 1.5;\n    }\n  }\n  \n  &-metrics {\n    display: flex;\n    justify-content: space-between;\n    margin-bottom: $spacing-md;\n    font-size: $font-size-xs;\n    color: $color-text-light;\n    \n    i {\n      color: $color-primary;\n      margin-right: $spacing-xs;\n    }\n  }\n  \n  &-actions {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n  }\n  \n  &-button {\n    background: $color-primary;\n    color: white;\n    border: none;\n    padding: $spacing-sm $spacing-md;\n    border-radius: $border-radius-sm;\n    text-decoration: none;\n    font-size: $font-size-sm;\n    transition: background $transition-default;\n    \n    &:hover {\n      background: $color-primary-dark;\n    }\n  }\n  \n  &-favorite {\n    background: none;\n    border: none;\n    color: #999;\n    font-size: $font-size-lg;\n    cursor: pointer;\n    transition: transform $transition-fast;\n    \n    &:hover {\n      transform: scale(1.1);\n    }\n  }\n}\n\n// Product card\n.product-card {\n  @include card;\n  \n  img {\n    width: 100%;\n    height: 200px;\n    object-fit: cover;\n  }\n  \n  &-content {\n    padding: $spacing-lg;\n  }\n  \n  h4 {\n    font-size: $font-size-lg;\n    margin-bottom: $spacing-sm;\n    color: $color-secondary;\n  }\n  \n  p {\n    margin-bottom: $spacing-md;\n    color: $color-text-light;\n  }\n  \n  .price {\n    font-weight: bold;\n    color: $color-primary;\n  }\n}\n',
        '_forms.scss': '// Form styles\n\n// Form group\n.form-group {\n  margin-bottom: $spacing-md;\n  display: flex;\n  flex-direction: column;\n  \n  label {\n    font-size: $font-size-sm;\n    margin-bottom: $spacing-xs;\n    color: $color-text-light;\n  }\n}\n\n// Form control\n.form-control {\n  @include form-control;\n}\n\n// Carbon form\n.carbon-form {\n  margin-top: $spacing-md;\n  width: 100%;\n  \n  .form-group {\n    margin-bottom: $spacing-md;\n  }\n  \n  button.btn.btn-success {\n    padding: $spacing-sm $spacing-md;\n    border: none;\n    border-radius: $border-radius-sm;\n    background: #28a745;\n    color: white;\n    font-size: $font-size-sm;\n    cursor: pointer;\n    transition: background $transition-default;\n    \n    &:hover {\n      background: #218838;\n    }\n  }\n}\n\n// Auth form\n.auth-form {\n  .form-group {\n    margin-bottom: $spacing-md;\n  }\n  \n  .form-control {\n    width: 100%;\n    padding: $spacing-md $spacing-md;\n    border: 1px solid $color-border;\n    border-radius: $border-radius-md;\n    font-size: $font-size-md;\n    transition: border-color $transition-default;\n    \n    &:focus {\n      border-color: $color-primary;\n      outline: none;\n    }\n  }\n  \n  .auth-submit-btn {\n    width: 100%;\n    background: $color-primary;\n    color: white;\n    border: none;\n    padding: $spacing-md;\n    border-radius: $border-radius-md;\n    font-size: $font-size-md;\n    cursor: pointer;\n    transition: background $transition-default, transform $transition-fast;\n    margin-top: $spacing-md;\n    \n    &:hover {\n      background: $color-primary-dark;\n      transform: translateY(-2px);\n    }\n  }\n}\n\n// Contact form\n.contact-form {\n  display: flex;\n  flex-direction: column;\n  gap: $spacing-md;\n  \n  .input-row {\n    display: flex;\n    gap: $spacing-md;\n    flex-wrap: wrap;\n  }\n  \n  .submit-button {\n    background: $color-secondary;\n    color: white;\n    border: none;\n    padding: $spacing-md $spacing-lg;\n    border-radius: $border-radius-sm;\n    cursor: pointer;\n    font-size: $font-size-md;\n    \n    &:hover {\n      background: #333;\n    }\n  }\n}\n',
        '_modals.scss': '// Modal styles\n\n.modal {\n  display: none;\n  position: fixed;\n  z-index: 1000;\n  left: 0;\n  top: 0;\n  width: 100%;\n  height: 100%;\n  overflow: auto;\n  background-color: rgba(0, 0, 0, 0.5);\n  \n  &-content {\n    background-color: white;\n    margin: 10% auto;\n    padding: $spacing-xl;\n    border-radius: $border-radius-md;\n    box-shadow: $shadow-lg;\n    max-width: 600px;\n    width: 90%;\n    position: relative;\n  }\n  \n  .close-modal {\n    position: absolute;\n    top: $spacing-md;\n    right: $spacing-lg;\n    font-size: $font-size-xl;\n    color: #aaa;\n    cursor: pointer;\n    transition: color $transition-default;\n    \n    &:hover {\n      color: $color-secondary;\n    }\n  }\n  \n  h2 {\n    margin-bottom: $spacing-lg;\n    color: $color-secondary;\n  }\n  \n  .form-group {\n    margin-bottom: $spacing-md;\n  }\n  \n  label {\n    display: block;\n    margin-bottom: $spacing-sm;\n    color: $color-text-light;\n  }\n  \n  input, select, textarea {\n    width: 100%;\n    padding: $spacing-md;\n    border: 1px solid $color-border;\n    border-radius: $border-radius-sm;\n    font-size: $font-size-md;\n  }\n  \n  .submit-btn {\n    background: $color-primary;\n    color: white;\n    border: none;\n    padding: $spacing-md $spacing-lg;\n    border-radius: $border-radius-sm;\n    font-size: $font-size-md;\n    cursor: pointer;\n    transition: all $transition-default ease;\n    width: 100%;\n    margin-top: $spacing-md;\n    \n    &:hover {\n      background: $color-primary-dark;\n    }\n  }\n}\n',
    },
    'pages': {
        '_home.scss': '// Home page styles\n\n// Content container for sections\n.content-container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: 0 $spacing-xl;\n  text-align: center;\n}\n\n// Welcome section styling\n#welcome-section {\n  background-color: #e8f5e9;\n  color: $color-primary;\n}\n\n.welcome-content {\n  max-width: 800px;\n  margin: 0 auto;\n  text-align: center;\n  \n  h1 {\n    font-size: $font-size-hero;\n    margin-bottom: $spacing-md;\n  }\n}\n\n.tagline {\n  font-size: $font-size-xl;\n  margin-bottom: $spacing-xl;\n}\n\n.cta-buttons {\n  display: flex;\n  justify-content: center;\n  gap: $spacing-md;\n  margin-top: $spacing-xl;\n  \n  @include respond-to(md) {\n    flex-direction: column;\n    align-items: center;\n  }\n}\n\n// Food forest section styling\n.food-forest-content {\n  display: flex;\n  flex-wrap: wrap;\n  gap: $spacing-xl;\n  margin-top: $spacing-xl;\n  align-items: center;\n  \n  .food-forest-text {\n    flex: 1;\n    min-width: 300px;\n    text-align: left;\n    \n    p {\n      margin-bottom: $spacing-md;\n      line-height: 1.6;\n    }\n  }\n  \n  .food-forest-image {\n    flex: 1;\n    min-width: 300px;\n    \n    img {\n      max-width: 100%;\n      height: auto;\n      border-radius: $border-radius-md;\n      box-shadow: $shadow-lg;\n    }\n  }\n  \n  @include respond-to(md) {\n    flex-direction: column;\n    text-align: center;\n    \n    .food-forest-text {\n      text-align: center;\n    }\n  }\n}\n\n// Benefit sections styling\n.benefit-section {\n  text-align: center;\n}\n\n.benefit-content {\n  max-width: 700px;\n  margin: 0 auto;\n  \n  .benefit-icon {\n    font-size: 4rem;\n    margin-bottom: $spacing-lg;\n    display: inline-block;\n    color: $color-primary;\n  }\n  \n  h2 {\n    font-size: $font-size-xxl;\n    margin-bottom: $spacing-md;\n  }\n  \n  p {\n    font-size: $font-size-lg;\n    line-height: 1.6;\n    color: $color-text-light;\n  }\n  \n  @include respond-to(md) {\n    .benefit-icon {\n      font-size: 3rem;\n    }\n    \n    h2 {\n      font-size: $font-size-xl;\n    }\n    \n    p {\n      font-size: $font-size-md;\n    }\n  }\n}\n\n// Section styling\n.section {\n  display: flex;\n  flex-direction: column;\n  justify-content: center;\n  align-items: center;\n  height: 100vh;\n  text-align: center;\n  font-size: $font-size-hero;\n  overflow: hidden;\n  position: relative;\n  transition: background-color $transition-slow;\n  \n  &#section1 {\n    background: url("/static/images/fresh-vegetables.jpg") no-repeat center center;\n    background-size: cover;\n    background-attachment: fixed;\n    background-color: #dcf5f2;\n    color: #000;\n    position: relative;\n    \n    .overlay {\n      background: rgba(255, 255, 255, 0.75);\n      padding: $spacing-xl;\n      border-radius: $border-radius-md;\n      max-width: 800px;\n      text-align: center;\n    }\n  }\n}\n\n// Line separator\n.line {\n  width: 150px;\n  height: 4px;\n  background: currentColor;\n  margin: $spacing-xl auto;\n  transition: width $transition-slow;\n}\n\n// Why us content\n.why-us-content {\n  max-width: 800px;\n  margin: 0 auto;\n  \n  img {\n    max-width: 100%;\n    height: auto;\n  }\n  \n  p {\n    font-size: $font-size-md;\n    margin-bottom: $spacing-md;\n  }\n}\n',
        '_forest.scss': '// Forest page styles\n\n// Food Forest Library\n.food-forest-library {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: $spacing-xl $spacing-md;\n}\n\n// Hero Banner for Forest Library\n.forest-library-hero {\n  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url("/static/images/hero_pears.jpg");\n  background-size: cover;\n  background-position: center;\n  color: white;\n  text-align: center;\n  padding: 5rem $spacing-xl;\n  margin-bottom: $spacing-xl;\n  border-radius: $border-radius-md;\n  \n  .forest-hero-content {\n    max-width: 800px;\n    margin: 0 auto;\n    \n    h1 {\n      font-size: $font-size-hero;\n      margin-bottom: $spacing-md;\n      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);\n    }\n    \n    p {\n      font-size: $font-size-lg;\n      margin-bottom: $spacing-lg;\n      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);\n    }\n  }\n}\n\n// Search and Filter Section\n.search-filter-section {\n  background: $color-background-light;\n  padding: $spacing-lg;\n  border-radius: $border-radius-md;\n  margin-bottom: $spacing-xl;\n  box-shadow: $shadow-sm;\n  \n  .search-container {\n    display: inline-flex;\n    align-items: center;\n    border: 1px solid $color-border;\n    max-width: 500px;\n    width: 100%;\n    border-radius: $border-radius-sm;\n    overflow: hidden;\n    box-shadow: $shadow-sm;\n    \n    input {\n      flex: 1;\n      padding: $spacing-md;\n      border: none;\n      outline: none;\n      font-size: $font-size-md;\n    }\n    \n    button {\n      border-radius: $border-radius-sm;\n      margin-right: $spacing-xs;\n      background: $color-primary;\n      color: white;\n      border: none;\n      padding: $spacing-md $spacing-md;\n      cursor: pointer;\n      transition: background $transition-default;\n      \n      &:hover {\n        background: $color-primary-dark;\n      }\n    }\n  }\n  \n  .search-icon {\n    margin: 0 $spacing-sm 0 $spacing-md;\n    color: $color-text-light;\n  }\n  \n  .filter-options {\n    display: flex;\n    flex-wrap: wrap;\n    gap: $spacing-md;\n    margin-top: $spacing-lg;\n    \n    .filter-group {\n      flex: 1;\n      min-width: 200px;\n      \n      label {\n        display: block;\n        margin-bottom: $spacing-sm;\n        font-weight: 500;\n        color: $color-text-light;\n      }\n      \n      select {\n        width: 100%;\n        padding: $spacing-sm;\n        border: 1px solid $color-border;\n        border-radius: $border-radius-sm;\n        background-color: white;\n        font-size: $font-size-sm;\n      }\n    }\n  }\n}\n\n// Forest Page Styles\n.forest-hero {\n  position: relative;\n  width: 100%;\n  height: 60vh;\n  background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url("/static/images/hero_pears.jpg");\n  background-size: cover;\n  background-position: center;\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  color: white;\n  text-align: center;\n  \n  &-content {\n    max-width: 800px;\n    padding: $spacing-xl;\n    \n    h1 {\n      font-size: $font-size-hero;\n      margin-bottom: $spacing-sm;\n      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);\n    }\n  }\n}\n\n.forest-location {\n  font-size: $font-size-lg;\n  margin-bottom: $spacing-xl;\n  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);\n}\n\n// Inventory Section\n.inventory-container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: $spacing-xxl $spacing-md;\n  \n  h2 {\n    font-size: $font-size-xxl;\n    margin-bottom: $spacing-xl;\n    text-align: center;\n    color: $color-secondary;\n  }\n}\n\n.inventory-layout {\n  display: grid;\n  grid-template-columns: 1fr;\n  gap: $spacing-xxl;\n  margin-bottom: $spacing-xxl;\n}\n\n.featured-product {\n  display: flex;\n  flex-wrap: wrap;\n  background: $color-background-light;\n  border-radius: $border-radius-md;\n  overflow: hidden;\n  box-shadow: $shadow-md;\n  \n  img {\n    width: 100%;\n    max-width: 500px;\n    height: auto;\n    object-fit: cover;\n  }\n  \n  &-info {\n    flex: 1;\n    min-width: 300px;\n    padding: $spacing-xl;\n    \n    h3 {\n      font-size: $font-size-xl;\n      margin-bottom: $spacing-md;\n      color: $color-primary;\n    }\n    \n    p {\n      margin-bottom: $spacing-lg;\n      line-height: 1.6;\n      color: $color-text-light;\n    }\n  }\n}\n\n.view-product-btn {\n  display: inline-block;\n  background: $color-primary;\n  color: white;\n  padding: $spacing-sm $spacing-lg;\n  border-radius: $border-radius-sm;\n  text-decoration: none;\n  transition: all $transition-default ease;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n  }\n}\n\n.product-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));\n  gap: $spacing-xl;\n}\n',
        '_profile.scss': '// Profile page styles\n\n// Profile Page Wrapper\n.profile-page {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: $spacing-xl $spacing-md;\n}\n\n// Top Section: 2 columns\n.profile-top {\n  display: flex;\n  flex-wrap: wrap;\n  gap: $spacing-xl;\n  margin-bottom: $spacing-xl;\n}\n\n// Forest Details Column\n.forest-details {\n  flex: 1;\n  min-width: 280px;\n  background: #eee;\n  padding: $spacing-md;\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  text-align: center;\n  \n  img {\n    max-width: 100%;\n    height: auto;\n    margin-bottom: $spacing-md;\n    border: 1px solid $color-border;\n    border-radius: $border-radius-sm;\n  }\n  \n  h2 {\n    margin-bottom: $spacing-sm;\n  }\n}\n\n// Details Column\n.details-wrapper {\n  flex: 2;\n  min-width: 280px;\n  background: #eee;\n  padding: $spacing-md;\n  width: 30%;\n  max-width: 400px;\n  \n  h2 {\n    margin-bottom: $spacing-md;\n  }\n}\n\n// Metrics Box\n.metrics-box {\n  background: #ccc;\n  padding: $spacing-md;\n  margin-top: $spacing-md;\n  \n  .metrics-header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    margin-bottom: $spacing-md;\n    \n    h3 {\n      margin: 0;\n    }\n  }\n  \n  .metrics-content p {\n    margin: $spacing-sm 0;\n  }\n  \n  .metrics-section {\n    cursor: pointer;\n  }\n}\n\n// Inventory Section\n.inventory-section {\n  background: #ddd;\n  padding: $spacing-md;\n  margin-bottom: $spacing-xl;\n  \n  .inventory-header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    margin-bottom: $spacing-md;\n    \n    h2 {\n      margin: 0;\n    }\n  }\n  \n  .inventory-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n    gap: $spacing-md;\n    background: #fdf2f2;\n    padding: $spacing-md;\n  }\n}\n\n// Profile Container\n.profile-container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: $spacing-xl $spacing-md;\n}\n\n.profile-top-section {\n  display: flex;\n  flex-wrap: wrap;\n  gap: $spacing-xl;\n  margin-bottom: $spacing-xl;\n}\n\n.profile-card {\n  background: white;\n  border-radius: $border-radius-md;\n  box-shadow: $shadow-md;\n  overflow: hidden;\n}\n\n.forest-details-card {\n  flex: 1;\n  min-width: 300px;\n  background: $color-background-light;\n  \n  h2 {\n    padding: $spacing-lg;\n    margin: 0;\n    font-size: $font-size-xl;\n    border-bottom: 1px solid $color-border;\n  }\n  \n  &-content {\n    padding: $spacing-lg;\n  }\n}\n\n.forest-image {\n  margin-bottom: $spacing-lg;\n  \n  img {\n    width: 100%;\n    height: auto;\n    border-radius: $border-radius-md;\n    object-fit: cover;\n  }\n}\n\n.forest-info {\n  h3 {\n    font-size: $font-size-xl;\n    margin-bottom: $spacing-sm;\n    color: $color-secondary;\n  }\n  \n  .forest-location {\n    color: $color-text-light;\n    margin-bottom: $spacing-lg;\n  }\n}\n\n.forest-actions {\n  margin-top: $spacing-md;\n}\n\n.edit-forest-btn {\n  background: $color-primary;\n  color: white;\n  border: none;\n  padding: $spacing-sm $spacing-md;\n  border-radius: $border-radius-sm;\n  font-size: $font-size-sm;\n  cursor: pointer;\n  transition: all $transition-default ease;\n  display: flex;\n  align-items: center;\n  gap: $spacing-sm;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n  }\n}\n',
        '_business.scss': '// Business profile styles\n\nbody.business-profile-page {\n  background-color: #1a1a1a;\n}\n\n.profile-container {\n  max-width: $breakpoint-xl;\n  margin: 0 auto;\n  padding: $spacing-xl $spacing-md;\n  background-color: white;\n}\n\n.profile-header {\n  background-color: #000;\n  color: white;\n  padding: $spacing-md $spacing-xl;\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  \n  h1 {\n    margin: 0;\n    font-size: $font-size-xl;\n  }\n}\n\n.profile-nav {\n  display: flex;\n  gap: $spacing-xl;\n  align-items: center;\n  \n  a {\n    color: white;\n    text-decoration: none;\n  }\n  \n  @include respond-to(md) {\n    gap: $spacing-md;\n  }\n}\n\n.sign-out-btn {\n  background-color: white;\n  color: black;\n  padding: $spacing-sm $spacing-md;\n  border-radius: $border-radius-sm;\n  text-decoration: none;\n}\n\n.profile-content {\n  display: flex;\n  gap: $spacing-xl;\n  margin-top: $spacing-xl;\n  \n  @include respond-to(md) {\n    flex-direction: column;\n  }\n}\n\n.business-details-card {\n  background-color: #f0f0f0;\n  padding: $spacing-lg;\n  border-radius: $border-radius-sm;\n  width: 30%;\n  \n  h2 {\n    margin-top: 0;\n    margin-bottom: $spacing-md;\n  }\n  \n  @include respond-to(md) {\n    width: 100%;\n  }\n}\n\n.business-image {\n  border: 2px solid #4a90e2;\n  border-radius: $border-radius-sm;\n  overflow: hidden;\n  margin-bottom: $spacing-md;\n  \n  img {\n    width: 100%;\n    height: auto;\n    display: block;\n  }\n}\n\n.about-section {\n  flex: 1;\n  \n  h2 {\n    font-size: $font-size-xxl;\n    margin-top: 0;\n    margin-bottom: $spacing-sm;\n  }\n  \n  .subtitle {\n    color: $color-text-light;\n    margin-bottom: $spacing-lg;\n  }\n}\n\n.food-forests-section {\n  background-color: #f0f0f0;\n  padding: $spacing-lg;\n  border-radius: $border-radius-sm;\n  margin-top: $spacing-xl;\n  \n  h2 {\n    margin-top: 0;\n    margin-bottom: $spacing-lg;\n  }\n}\n\n.forests-grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: $spacing-md;\n  background-color: white;\n  padding: $spacing-lg;\n  border-radius: $border-radius-sm;\n  \n  @include respond-to(md) {\n    grid-template-columns: repeat(2, 1fr);\n  }\n  \n  @include respond-to(sm) {\n    grid-template-columns: 1fr;\n  }\n}\n\n.forest-card {\n  background-color: #f0f0f0;\n  padding: $spacing-md;\n  border-radius: $border-radius-sm;\n  \n  h3 {\n    margin-top: 0;\n    margin-bottom: $spacing-sm;\n  }\n}\n\n.forest-image {\n  width: 100%;\n  height: 100px;\n  object-fit: cover;\n  border-radius: $border-radius-sm;\n  margin-bottom: $spacing-sm;\n}\n\n.explore-btn {\n  background-color: #000;\n  color: white;\n  padding: $spacing-xs $spacing-sm;\n  border-radius: $border-radius-sm;\n  text-decoration: none;\n  font-size: $font-size-xs;\n  display: inline-block;\n  margin-top: $spacing-sm;\n}\n\n// About Section Styling\n.about-header {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  margin-bottom: $spacing-md;\n}\n\n.edit-btn {\n  background: $color-primary;\n  color: white;\n  border: none;\n  padding: $spacing-sm $spacing-md;\n  border-radius: $border-radius-sm;\n  font-size: $font-size-sm;\n  cursor: pointer;\n  transition: all $transition-default ease;\n  display: flex;\n  align-items: center;\n  gap: $spacing-sm;\n  \n  &:hover {\n    background: $color-primary-dark;\n    transform: translateY(-2px);\n  }\n}\n\n#about-content {\n  line-height: 1.6;\n  color: $color-secondary;\n}\n',
        '_auth.scss': '// Authentication pages styles\n\n.auth-container {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  min-height: calc(100vh - 150px);\n  padding: $spacing-xl $spacing-md;\n  background-color: $color-background-light;\n}\n\n.auth-card {\n  background: white;\n  border-radius: $border-radius-md;\n  box-shadow: $shadow-lg;\n  width: 100%;\n  max-width: 450px;\n  padding: $border-radius-md;
  box-shadow: $shadow-lg;
  width: 100%;
  max-width: 450px;
  padding: $spacing-xxl;
}

.auth-header {
  text-align: center;
  margin-bottom: $spacing-xl;
  
  h2 {
    font-size: $font-size-xl;
    color: $color-secondary;
    margin-bottom: $spacing-sm;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-sm;
  }
}

.auth-welcome {
  color: $color-text-light;
  font-size: $font-size-sm;
}

.account-type-selector {
  display: flex;
  margin-bottom: $spacing-xl;
  border: 1px solid $color-border;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.account-type-btn {
  flex: 1;
  background: none;
  border: none;
  padding: $spacing-md;
  font-size: $font-size-md;
  cursor: pointer;
  transition: all $transition-default ease;
  
  &.active {
    background: $color-primary;
    color: white;
  }
  
  @include respond-to(sm) {
    padding: $spacing-sm $spacing-xs;
    font-size: $font-size-sm;
  }
}

.forgot-password {
  text-align: right;
  margin-top: $spacing-sm;
  
  a {
    color: $color-primary;
    font-size: $font-size-xs;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.auth-divider {
  display: flex;
  align-items: center;
  margin: $spacing-xl 0;
  color: #999;
  font-size: $font-size-sm;
  
  &::before,
  &::after {
    content: "";
    flex: 1;
    height: 1px;
    background: $color-border;
  }
  
  span {
    padding: 0 $spacing-md;
  }
}

.social-login {
  display: flex;
  justify-content: center;
  margin-bottom: $spacing-xl;
}

.google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-md;
  background: white;
  border: 1px solid $color-border;
  padding: $spacing-md $spacing-lg;
  border-radius: $border-radius-md;
  font-size: $font-size-md;
  cursor: pointer;
  transition: background $transition-default, transform $transition-fast;
  
  &:hover {
    background: $color-background-light;
    transform: translateY(-2px);
  }
  
  img {
    width: 20px;
    height: 20px;
  }
}

.auth-footer {
  text-align: center;
  color: $color-text-light;
  font-size: $font-size-sm;
  
  a {
    color: $color-primary;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
',
        '_article.scss': '// Article page styles

.article-container {
  max-width: $breakpoint-xl;
  margin: 0 auto;
  padding: $spacing-xxl $spacing-md;
}

.comparison-article {
  background: white;
  border-radius: $border-radius-md;
  overflow: hidden;
  box-shadow: $shadow-md;
}

.article-header {
  padding: $spacing-xxl;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
  
  h1 {
    font-size: $font-size-xxl;
    margin-bottom: $spacing-md;
    color: $color-secondary;
  }
}

.article-subtitle {
  font-size: $font-size-lg;
  color: $color-text-light;
  line-height: 1.6;
}

.visual-comparison {
  padding: $spacing-xl;
  background: $color-background-light;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: $spacing-xl;
  margin-bottom: $spacing-xxl;
  
  @include respond-to(md) {
    grid-template-columns: 1fr;
  }
}

.comparison-column {
  background: white;
  padding: $spacing-xl;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
  
  h2 {
    font-size: $font-size-xl;
    margin-bottom: $spacing-lg;
    text-align: center;
    color: $color-secondary;
  }
}

.product-image {
  text-align: center;
  margin-bottom: $spacing-lg;
  
  img {
    max-width: 200px;
    height: auto;
    border-radius: $border-radius-md;
  }
}

.price-tag {
  text-align: center;
  margin-bottom: $spacing-xl;
  font-size: $font-size-lg;
  color: $color-secondary;
}

.price-value {
  font-weight: 500;
}

.detailed-explanation {
  padding: $spacing-xxl;
  
  h2 {
    font-size: $font-size-xl;
    margin-bottom: $spacing-xl;
    color: $color-secondary;
    text-align: center;
  }
}

.explanation-block {
  margin-bottom: $spacing-xxl;
  
  h3 {
    font-size: $font-size-lg;
    margin-bottom: $spacing-md;
    color: $color-primary;
  }
  
  p {
    margin-bottom: $spacing-md;
    line-height: 1.6;
    color: $color-text-light;
  }
  
  ul {
    padding-left: $spacing-lg;
    margin-bottom: $spacing-md;
  }
  
  li {
    margin-bottom: $spacing-sm;
    line-height: 1.6;
    color: $color-text-light;
  }
}

.article-cta {
  padding: $spacing-xxl;
  background: #e8f5e9;
  text-align: center;
  
  h2 {
    font-size: $font-size-xl;
    margin-bottom: $spacing-md;
    color: $color-primary;
  }
  
  p {
    margin-bottom: $spacing-xl;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    color: $color-text-light;
    line-height: 1.6;
  }
}
',
        '_product.scss': '// Product detail page styles

.product-detail-container {
  max-width: $breakpoint-xl;
  margin: 0 auto;
  padding: $spacing-xxl $spacing-md;
}

.product-overview {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xxl;
  margin-bottom: $spacing-xxl;
  
  @include respond-to(md) {
    flex-direction: column;
  }
}

.product-image {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
  
  img {
    width: 100%;
    height: auto;
    border-radius: $border-radius-md;
    box-shadow: $shadow-md;
  }
  
  @include respond-to(md) {
    max-width: 100%;
  }
}

.product-info {
  flex: 1;
  min-width: 300px;
  
  h1 {
    font-size: $font-size-xxl;
    margin-bottom: $spacing-sm;
    color: $color-secondary;
  }
}

.product-price {
  font-size: $font-size-xl;
  font-weight: 500;
  color: $color-primary;
  margin-bottom: $spacing-lg;
}

.product-description {
  margin-bottom: $spacing-xl;
  
  p {
    line-height: 1.6;
    color: $color-text-light;
  }
}

.product-actions {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
  
  @include respond-to(sm) {
    flex-direction: column;
  }
}

.add-to-cart-btn {
  background: $color-primary;
  color: white;
  border: none;
  padding: $spacing-md $spacing-xl;
  border-radius: $border-radius-sm;
  font-size: $font-size-md;
  cursor: pointer;
  transition: all $transition-default ease;
  
  &:hover {
    background: $color-primary-dark;
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

.favorite-btn {
  background: white;
  color: $color-text-light;
  border: 1px solid $color-border;
  width: 48px;
  height: 48px;
  border-radius: $border-radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-lg;
  cursor: pointer;
  transition: all $transition-default ease;
  
  &:hover {
    color: #e74c3c;
    border-color: #e74c3c;
  }
  
  @include respond-to(sm) {
    width: 100%;
  }
}

.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-lg;
  color: $color-text-light;
  
  span {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }
  
  i {
    color: $color-primary;
  }
}

// True Value Assessment Section
.true-value-section {
  margin-bottom: $spacing-xxl;
  padding: $spacing-xxl;
  background: $color-background-light;
  border-radius: $border-radius-md;
  
  h2 {
    font-size: $font-size-xl;
    margin-bottom: $spacing-md;
    color: $color-secondary;
  }
  
  > p {
    margin-bottom: $spacing-xl;
    color: $color-text-light;
    line-height: 1.6;
    max-width: 800px;
  }
}

.value-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xl;
}

.cost-breakdown {
  flex: 1;
  min-width: 300px;
  
  h3 {
    font-size: $font-size-lg;
    margin-bottom: $spacing-lg;
    color: $color-secondary;
  }
}

.chart-container {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xl;
}

.pie-chart {
  flex: 1;
  min-width: 200px;
  max-width: 300px;
}

.chart-placeholder {
  width: 100%;
  height: auto;
  border-radius: $border-radius-md;
  background: #eee;
}

.chart-legend {
  flex: 1;
  min-width: 200px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: $border-radius-sm;
}

.legend-label {
  color: $color-text-light;
}
',
    },
    'main.scss': '// Main SCSS file that imports all partials\n\n// Abstracts\n@import "abstracts/variables";\n@import "abstracts/functions";\n@import "abstracts/mixins";\n\n// Base styles\n@import "base/reset";\n@import "base/typography";\n@import "base/utilities";\n\n// Layout\n@import "layout/grid";\n@import "layout/navbar";\n@import "layout/footer";\n\n// Components\n@import "components/buttons";\n@import "components/cards";\n@import "components/forms";\n@import "components/modals";\n\n// Pages\n@import "pages/home";\n@import "pages/forest";\n@import "pages/profile";\n@import "pages/business";\n@import "pages/auth";\n@import "pages/article";\n@import "pages/product";\n',
}

def create_scss_structure():
    """Create the SCSS directory structure and files."""
    # Create the main SCSS directory
    if not os.path.exists(SCSS_DIR):
        os.makedirs(SCSS_DIR)
        print(f"Created directory: {SCSS_DIR}")
    
    # Create subdirectories and files
    for subdir, files in SCSS_STRUCTURE.items():
        if subdir != 'main.scss':  # Skip main.scss as it's not a directory
            subdir_path = os.path.join(SCSS_DIR, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
                print(f"Created directory: {subdir_path}")
            
            # Create files in the subdirectory
            for filename, content in files.items():
                file_path = os.path.join(subdir_path, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"Created file: {file_path}")
        else:
            # Create main.scss in the root SCSS directory
            main_scss_path = os.path.join(SCSS_DIR, 'main.scss')
            with open(main_scss_path, 'w') as f:
                f.write(files)
            print(f"Created file: {main_scss_path}")

def convert_css_to_scss():
    """Convert existing CSS files to SCSS if they exist."""
    if os.path.exists(CSS_DIR):
        print("Converting existing CSS files to SCSS...")
        
        # Get all CSS files
        css_files = [f for f in os.listdir(CSS_DIR) if f.endswith('.css')]
        
        for css_file in css_files:
            css_path = os.path.join(CSS_DIR, css_file)
            scss_file = css_file.replace('.css', '.scss')
            
            # Determine which SCSS partial to update
            if css_file == 'base.css':
                target_dir = os.path.join(SCSS_DIR, 'base')
                target_file = '_reset.scss'
            elif css_file == 'navbar.css':
                target_dir = os.path.join(SCSS_DIR, 'layout')
                target_file = '_navbar.scss'
            elif css_file == 'footer.css':
                target_dir = os.path.join(SCSS_DIR, 'layout')
                target_file = '_footer.scss'
            elif css_file == 'components.css':
                target_dir = os.path.join(SCSS_DIR, 'components')
                target_file = '_buttons.scss'  # Just update one component file as example
            elif css_file == 'home.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_home.scss'
            elif css_file == 'forest.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_forest.scss'
            elif css_file == 'profile.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_profile.scss'
            elif css_file == 'business.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_business.scss'
            elif css_file == 'auth.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_auth.scss'
            elif css_file == 'article.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_article.scss'
            elif css_file == 'product.css':
                target_dir = os.path.join(SCSS_DIR, 'pages')
                target_file = '_product.scss'
            else:
                # Skip files we don't have a mapping for
                print(f"Skipping {css_file} - no mapping defined")
                continue
            
            # Read the CSS content
            with open(css_path, 'r') as f:
                css_content = f.read()
            
            # Convert CSS to SCSS (basic conversion - just add variables)
            scss_content = css_content
            
            # Replace color values with variables
            scss_content = scss_content.replace('#2e7d32', '$color-primary')
            scss_content = scss_content.replace('#1b5e20', '$color-primary-dark')
            scss_content = scss_content.replace('#333', '$color-secondary')
            scss_content = scss_content.replace('#ddd', '$color-border')
            
            # Replace common spacing values with variables
            scss_content = scss_content.replace('0.25rem', '$spacing-xs')
            scss_content = scss_content.replace('0.5rem', '$spacing-sm')
            scss_content = scss_content.replace('1rem', '$spacing-md')
            scss_content = scss_content.replace('1.5rem', '$spacing-lg')
            scss_content = scss_content.replace('2rem', '$spacing-xl')
            scss_content = scss_content.replace('3rem', '$spacing-xxl')
            
            # Replace font sizes with variables
            scss_content = scss_content.replace('0.85rem', '$font-size-xs')
            scss_content = scss_content.replace('0.9rem', '$font-size-sm')
            scss_content = scss_content.replace('1rem', '$font-size-md')
            scss_content = scss_content.replace('1.2rem', '$font-size-lg')
            scss_content = scss_content.replace('1.5rem', '$font-size-xl')
            scss_content = scss_content.replace('2rem', '$font-size-xxl')
            scss_content = scss_content.replace('3rem', '$font-size-hero')
            
            # Add nesting where possible (this is a simple example and won't catch everything)
            # A more sophisticated conversion would require a CSS parser
            
            # Update the target SCSS file with some of the converted content
            target_path = os.path.join(target_dir, target_file)
            if os.path.exists(target_path):
                print(f"Note: Content from {css_file} can be manually integrated into {target_path}")
                # We don't automatically update the files as our structure is already set up
            else:
                print(f"Warning: Target file {target_path} not found")

def create_requirements_file():
    """Create a requirements.txt file with necessary packages."""
    requirements = [
        "# SCSS compilation requirements",
        "libsass==0.22.0",
        "watchdog==3.0.0",
        "Flask-Assets==2.1.0",  # Optional for Flask integration
    ]
    
    with open('requirements.txt', 'a') as f:
        f.write('\n'.join(requirements) + '\n')
    
    print("Updated requirements.txt with SCSS compilation packages")

def main():
    """Main function to set up the SCSS structure."""
    print("Setting up SCSS directory structure...")
    create_scss_structure()
    
    print("\nChecking for existing CSS files to convert...")
    convert_css_to_scss()
    
    print("\nCreating requirements file...")
    create_requirements_file()
    
    print("\nSCSS setup complete!")
    print("\nTo compile your SCSS files, run:")
    print("  python website/compile_sass.py")
    print("\nTo watch for changes and recompile automatically:")
    print("  python website/compile_sass.py --watch")
    
    print("\nMake sure to update your templates to reference the compiled CSS file:")
    print('  <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/main.css\') }}">')

if __name__ == "__main__":
    main()
