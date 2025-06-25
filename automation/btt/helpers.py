import time

def select_countries(automation_helper, country_list=None):
    """
    Select countries from a multi-list view using keyboard navigation.
    
    Args:
        automation_helper: ManualAutomationHelper instance for keyboard automation
        country_list: List of country names to select from the multi-list view
    
    Returns:
        bool: True if all countries were successfully selected, False otherwise
    """
    if not country_list or not automation_helper:
        print("❌ No country list provided or automation helper is None")
        return False
    
    try:
        print(f"🌍 Starting country selection for {len(country_list)} countries...")
        
        all_countries = [
            "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antigua",
            "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
            "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bonaire",
            "Bosnia-Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory",
            "British Virgin Islands", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia",
            "Cameroon", "Canada", "Canton and Enderbury Islands", "Cape Verde Islands", "Cayman Islands",
            "Central African Republic", "Chad", "Chile", "China", "Cocos (Keeling) Island", "Colombia", "Comoros",
            "Congo", "Cook Islands", "Costa Rica", "Cote DIvoire", "Croatia", "Cuba", "Curacao", "Cyprus", 
            "Czech Republic", "Democratic Republic of the Congo", "Djibouti", "Dominica", "Dominican Republic",
            "Dronning Maud Land", "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea",
            "Estonia", "Ethiopia", "Faeroe Islands", "Falkland Islands (Malvinas)", "Fiji", "Finland", "France",
            "French Guiana", "French Polynesia", "French Southern Territory", "Gabon", "Gambia", "Georgia",
            "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala",
            "Guinea", "Guinea Bissau", "Guyana", "Haiti", "Heard and McDonald Islands", "Honduras", "Hong Kong",
            "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica",
            "Japan", "Johnston Island", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait",
            "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
            "Luxembourg", "Macao", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
            "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Micronesia", "Midway Islands", "Moldova",
            "Monaco", "Mongolia", "Montenegro", "Monteserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
            "Nepal", "Netherlands", "Netherlands Antilles", "Neutral Zone", "New Caledonia", "New Zealand", "Nicaragua",
            "Niger", "Nigeria", "Niue", "Norfolk Ireland", "North Korea", "North Macedonia", "Northern Mariana Islands",
            "Norway", "Oman", "Pacific Islands", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea",
            "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "Romania",
            "Russia", "Rwanda", "Réunion", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
            "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
            "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "St. Barthélemy", "St. Eustatius and Saba",
            "St. Helena", "St. Kitts and Nevis", "St. Lucia", "St. Maarten", "St. Martin", "St. Pierre and Miquelon",
            "St. Vincent and the Grenadines", "Sudan", "Surinam", "Svalbard and Jan Mayen Islands", "Swaziland", "Sweden",
            "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau Island", "Tonga",
            "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos", "Tuvalu", "Uganda", "Ukraine",
            "United Arab Emirates (UAE)", "United Kingdom (UK)", "United States (US)", "Uruguay", "US Minor Outlying Islands",
            "US Misc. Pacific Islands", "US Virgin Islands", "Uzbekistan", "Vanuatu", "Vatican City State", "Venezuela",
            "Vietnam", "Virgin Islands", "Wake Island", "Wallis and Futuna Islands", "Western Sahara", "Western Samoa",
            "Yemen Arab Republic", "Zambia", "Zimbabwe"
        ]
        
        # Create a working copy of all countries to track removals
        remaining_countries = all_countries.copy()
        current_position = 0  # Currently highlighted position (0-based, starting at Afghanistan)
        
        # Convert country_list to a set for faster lookups
        countries_to_select = set(country_list)
        selected_count = 0
        
        print(f"📍 Starting at position {current_position} ('{remaining_countries[current_position]}')")
        
        # Process each country in the remaining list
        while remaining_countries and selected_count < len(country_list):
            current_country = remaining_countries[current_position]
            
            # Check if current country should be selected
            if current_country in countries_to_select:
                print(f"✅ Selecting '{current_country}' at position {current_position}")
                
                # Press spacebar to select the country
                success = automation_helper.keys("{space}")
                if not success:
                    print(f"❌ Failed to select '{current_country}'")
                    return False
                
                time.sleep(0.1)  # Small delay after selection
                
                # Remove the selected country from remaining list
                remaining_countries.pop(current_position)
                selected_count += 1
                
                # Adjust current position after removal
                # If we removed the last item, move to previous position
                if current_position >= len(remaining_countries) and remaining_countries:
                    current_position = len(remaining_countries) - 1
                    # Move cursor to the new last position
                    automation_helper.keys("{up}")
                    time.sleep(0.05)
                # If list is empty, we're done
                elif not remaining_countries:
                    break
                # Otherwise, the current position now points to the next item
                # No navigation needed as the cursor will be on the next item
                
                print(f"🔄 Remaining countries: {len(remaining_countries)}, Position: {current_position}")
                
            else:
                # Current country not in selection list, move to next
                if current_position < len(remaining_countries) - 1:
                    # Move down if not at the end
                    current_position += 1
                    success = automation_helper.keys("{down}")
                    if not success:
                        print(f"❌ Failed to navigate down from '{current_country}'")
                        return False
                    time.sleep(0.05)
                else:
                    # At the end of list, check if we missed any countries
                    missing_countries = countries_to_select - set([c for c in all_countries if c not in remaining_countries])
                    if missing_countries:
                        print(f"⚠️ Reached end of list, but still need to select: {missing_countries}")
                        # Reset to beginning and continue searching
                        # Move to top of list
                        for _ in range(current_position):
                            automation_helper.keys("{up}")
                            time.sleep(0.02)
                        current_position = 0
                    else:
                        # All countries selected, break
                        break
        
        # Verify all countries were selected
        if selected_count == len(country_list):
            print(f"✅ Successfully selected all {selected_count} countries")
            
            # # Final step: Press Tab twice and Enter once
            # print("🎯 Completing selection: Tab -> Tab -> Enter")
            # automation_helper.keys("{tab}")
            # time.sleep(0.1)
            # automation_helper.keys("{tab}")
            # time.sleep(0.1)
            # automation_helper.keys("{enter}")
            # time.sleep(0.2)
            
            return True
        else:
            missing_countries = countries_to_select - set([c for c in all_countries if c not in remaining_countries])
            print(f"❌ Only selected {selected_count}/{len(country_list)} countries. Missing: {missing_countries}")
            return False
            
    except Exception as e:
        print(f"❌ Error during country selection: {e}")
        return False