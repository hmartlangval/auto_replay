import time

from utils.image_scanner import scan_for_image
from utils.windows_automation import ManualAutomationHelper

def start_questionnaire(automator, questionnaire_window_title: str):
    """
    Fill a questionnaire with the given name.
    """
    # What we should see now is a tabbed UI and first tab is highlighted
    # we are looking for a 2nd tab, we ensure we click the right tab by scanning for the unfocussed tab image
    # Lets scan for image for starting button
    if not (btn_start := scan_for_image("start-tse-test-session.png", automator.get_bbox(), threshold=0.8)):
        print("❌ No start button found")
        return None
    automator.click(btn_start)
    time.sleep(1)
    
    # this adds a edit button into the UI, we need to click on it
    # we scan for the edit button image
    if not (btn_edit := scan_for_image("edit-tse-test-session.png", automator.get_bbox(), threshold=0.8)):
        print("❌ No edit button found")
        return None
    automator.click(btn_edit)
    time.sleep(2)
    
    # Now we are in the Edit EMVCo L3 Test Session - Questionnaire window
    if not (edit_window := ManualAutomationHelper(target_window_title=questionnaire_window_title)):
        print(f"❌ No {questionnaire_window_title} window found")
        return None
    # Expected bounding box is BoundingRectangle:	{l:71 t:65 r:1270 b:707}
    edit_window.setup_window(bbox=(71, 65, 1270, 707))
    
     # Start the questionairres window
    # if not (edit_emvco_l3_test_session_window := start_questionnaire(current_parent_window, "Edit EMVCo L3 Test Session - Questionnaire")):
    #     return False
    
    # # What we should see now is a tabbed UI and first tab is highlighted
    # # we are looking for a 2nd tab, we ensure we click the right tab by scanning for the unfocussed tab image
    edit_answers_tab = scan_for_image("edit-answers.png", edit_window.get_bbox(), threshold=0.8)
    if edit_answers_tab:
        edit_window.click(edit_answers_tab)
        time.sleep(2)
    else:
        print("❌ No edit answers button found")
        return False
    
    return edit_window

def select_countries(automation_helper, country_list=None):
    """
    Select countries from a multi-list view using optimized keyboard navigation.
    Uses first-letter navigation to jump quickly to target countries, then fine-tunes with arrow keys.
    
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
        print(f"🌍 Starting optimized country selection for {len(country_list)} countries...")
        
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
        
        def find_country_index(country_name, country_list):
            """Find the index of a country in the list (case-insensitive)"""
            for i, country in enumerate(country_list):
                if country.lower() == country_name.lower():
                    return i
            return -1
        
        def get_first_country_with_letter(letter, country_list):
            """Get the first country that starts with the given letter"""
            letter_lower = letter.lower()
            for i, country in enumerate(country_list):
                if country.lower().startswith(letter_lower):
                    return i, country
            return -1, None
        
        def navigate_to_country_optimized(target_country, current_pos, available_countries):
            """
            Navigate to target country using correct UI behavior understanding
            Returns: (new_position, success)
            """
            target_index = find_country_index(target_country, available_countries)
            if target_index == -1:
                print(f"❌ Country '{target_country}' not found in list")
                return current_pos, False
            
            print(f"🎯 Navigating to '{target_country}' (index {target_index}) from current position {current_pos}")
            
            # Get current and target letter groups
            current_country = available_countries[current_pos]
            current_letter = current_country[0].upper()
            target_letter = target_country[0].upper()
            
            print(f"📍 Current: '{current_country}' (letter {current_letter}), Target: '{target_country}' (letter {target_letter})")
            
            # Only use letter navigation if we're in a different letter group
            if current_letter != target_letter:
                print(f"🔤 Different letter groups, typing '{target_letter}' to jump to that section")
                success = automation_helper.keys(target_letter)
                if not success:
                    print(f"❌ Failed to type letter '{target_letter}'")
                    return current_pos, False
                
                time.sleep(0.2)  # Allow UI to respond
                
                # After typing letter, we should be at the first country with that letter
                first_with_letter_pos, first_with_letter = get_first_country_with_letter(target_letter, available_countries)
                if first_with_letter_pos == -1:
                    print(f"⚠️ No country found starting with '{target_letter}'")
                    return current_pos, False
                
                current_pos = first_with_letter_pos
                print(f"📍 After letter jump, now at position {current_pos}: '{available_countries[current_pos]}'")
            else:
                print(f"🎯 Same letter group, using arrow keys only")
            
            # Now navigate within the same letter group using up/down arrows
            steps_needed = target_index - current_pos
            print(f"🔢 Need to move {steps_needed} steps ({'down' if steps_needed > 0 else 'up'})")
            
            if steps_needed > 0:
                # Move down
                for step in range(abs(steps_needed)):
                    success = automation_helper.keys("{down}")
                    if not success:
                        print(f"❌ Failed to move down at step {step+1}")
                        return current_pos, False
                    current_pos += 1
                    time.sleep(0.05)
                    
            elif steps_needed < 0:
                # Move up
                for step in range(abs(steps_needed)):
                    success = automation_helper.keys("{up}")
                    if not success:
                        print(f"❌ Failed to move up at step {step+1}")
                        return current_pos, False
                    current_pos -= 1
                    time.sleep(0.05)
            
            # We should now be at the target position
            final_country = available_countries[current_pos]
            print(f"📍 Final position {current_pos}: '{final_country}' (should be '{target_country}')")
            
            return current_pos, True
        
        def navigate_to_country_manual(target_country, current_pos, country_list):
            """Fallback manual navigation if first-letter method fails"""
            target_index = find_country_index(target_country, country_list)
            if target_index == -1:
                return current_pos, False
            
            steps_needed = target_index - current_pos
            if steps_needed > 0:
                for i in range(abs(steps_needed)):
                    automation_helper.keys("{down}")
                    time.sleep(0.05)
            elif steps_needed < 0:
                for i in range(abs(steps_needed)):
                    automation_helper.keys("{up}")
                    time.sleep(0.05)
            
            return target_index, True
        
        # Start selection process
        available_countries = all_countries.copy()  # Track remaining countries
        current_position = 0  # Start at first country (Afghanistan)
        selected_count = 0
        
        # Process each country to select
        for target_country in country_list:
            print(f"\n🎯 Selecting country {selected_count + 1}/{len(country_list)}: '{target_country}'")
            print(f"📊 Available countries: {len(available_countries)}, Current position: {current_position}")
            
            # Navigate to the target country using optimized method
            new_position, nav_success = navigate_to_country_optimized(
                target_country, current_position, available_countries
            )
            
            if not nav_success:
                print(f"❌ Failed to navigate to '{target_country}'")
                return False
            
            current_position = new_position
            
            # Select the country
            print(f"✅ Selecting '{target_country}' at position {current_position}")
            success = automation_helper.keys("{space}")
            if not success:
                print(f"❌ Failed to select '{target_country}'")
                return False
            
            print(f"⏳ Waiting for UI to update after selection...")
            time.sleep(1.5)  # Give UI time to update - remove item and adjust cursor position
            selected_count += 1
            
            # After selection: country is removed and cursor moves to position - 1
            removed_country = available_countries.pop(current_position)
            print(f"🗑️ Removed '{removed_country}' from available list")
            
            # Update current position: cursor moves to position - 1
            if current_position > 0:
                current_position -= 1
            else:
                current_position = 0  # Stay at 0 if we were at the beginning
            
            # Verify position doesn't exceed available countries
            if current_position >= len(available_countries) and available_countries:
                current_position = len(available_countries) - 1
            
            if available_countries and current_position < len(available_countries):
                current_country = available_countries[current_position]
                print(f"📍 After selection, cursor now at position {current_position}: '{current_country}'")
            else:
                print(f"📍 After selection, cursor at position {current_position} (list may be empty)")
            
            print(f"✅ Selected '{target_country}' successfully ({selected_count}/{len(country_list)})")
        
        print(f"\n🎉 Successfully selected all {selected_count} countries using optimized navigation!")
        return True
            
    except Exception as e:
        print(f"❌ Error during optimized country selection: {e}")
        return False