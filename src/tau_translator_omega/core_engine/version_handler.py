import semver
import logging
from typing import Optional, List, Tuple, Any
from packaging.specifiers import SpecifierSet, InvalidSpecifier

logger = logging.getLogger(__name__)

class VersionHandler:
    """Handles semantic version parsing and compatibility checks."""

    def __init__(self):
        self.errors: List[str] = []

    def _add_version_error(self, code: str, message: str, plugin_id: Optional[str] = None):
        error_msg = f"[{code}]"
        if plugin_id:
            error_msg += f" Plugin '{plugin_id}':"
        error_msg += f" {message}"
        self.errors.append(error_msg)
        logger.warning(error_msg)

    def parse_semver(self, version_string: Optional[str], context: str, plugin_id: Optional[str] = None) -> Optional[semver.VersionInfo]:
        if version_string is None or version_string.strip() == "":
            self._add_version_error(
                "VERSION_STRING_MISSING", 
                f"{context}: Version string is missing or empty.",
                plugin_id
            )
            return None
        try:
            return semver.VersionInfo.parse(version_string)
        except ValueError:
            self._add_version_error(
                "VERSION_STRING_MALFORMED",
                f"{context}: Version string '{version_string}' is not a valid semantic version.",
                plugin_id
            )
            return None

    def check_ilr_compatibility(
        self,
        core_ilr_semver: Optional[semver.VersionInfo],
        core_ilr_version_str: str, 
        plugin: Any 
    ) -> Tuple[bool, List[str]]:
        """
        Checks if the plugin's supported ILR versions are compatible with the core version.
        Relies on plugin object having 'id' and 'ilr_versions_supported: List[str]' attributes.
        Returns a tuple: (is_compatible: bool, error_messages: List[str]).
        """
        self.errors.clear()
        
        plugin_id = getattr(plugin, 'id', 'UnknownPlugin')

        if not core_ilr_semver:
            msg = f"Core ILR version '{core_ilr_version_str}' is invalid or not parsed. Cannot check compatibility for plugin '{plugin_id}'."
            self._add_version_error("CORE_ILR_INVALID_FOR_CHECK", msg, plugin_id)
            return False, list(self.errors)

        supported_versions_list = getattr(plugin, 'ilr_versions_supported', None)

        if not supported_versions_list: # Handles None or empty list
            logger.info(f"Plugin '{plugin_id}' specifies no ILR version constraints (ilr_versions_supported is missing or empty). Assuming compatibility.")
            return True, []

        if not isinstance(supported_versions_list, list):
            msg = f"Plugin '{plugin_id}' has an invalid 'ilr_versions_supported' attribute: expected a list, got {type(supported_versions_list).__name__}."
            self._add_version_error("ILR_VERSIONS_INVALID_TYPE", msg, plugin_id)
            return False, list(self.errors)

        found_compatible_version = False
        has_specifier_errors = False # Renamed for clarity

        for version_specifier_str in supported_versions_list:
            if not isinstance(version_specifier_str, str) or not version_specifier_str.strip():
                msg = f"Invalid item in 'ilr_versions_supported' for plugin '{plugin_id}': expected non-empty string, got '{version_specifier_str}'. Skipping this item."
                self._add_version_error("ILR_SPECIFIER_ITEM_INVALID", msg, plugin_id)
                has_specifier_errors = True
                continue
            
            current_spec_str = version_specifier_str.strip()
            # Check if it's a plain version string (e.g., "1.0.0", "1.2.3-alpha") vs. a full specifier (e.g., ">=1.0.0")
            # A simple check: if it doesn't start with common specifier characters and doesn't contain them mid-string for ranges.
            # This heuristic might need refinement for very complex specifiers not starting with operators.
            if not any(op in current_spec_str for op in ['=', '<', '>', '!', '~', ',']):
                # Attempt to parse as a simple version to ensure it's well-formed before prepending '=='
                # This also helps catch things like "abc" which are not versions.
                # parse_semver returns None if not a valid semver string, and adds an error.
                # However, SpecifierSet itself will raise InvalidSpecifier for non-versions, which is cleaner here.
                # Let's assume if no operator, it's intended as an exact version.
                current_spec_str = f"=={current_spec_str}"
                logger.info(f"Plain version string '{version_specifier_str}' detected. Interpreting as '{current_spec_str}'.")

            try:
                specifier_set = SpecifierSet(current_spec_str) # Use modified string
                # core_ilr_semver is a semver.VersionInfo object. Convert to string for SpecifierSet.contains().
                if specifier_set.contains(str(core_ilr_semver)):
                    found_compatible_version = True
                    logger.info(
                        f"Plugin '{plugin_id}' (ILR specifier: '{version_specifier_str}') is compatible with Core ILR {core_ilr_version_str}."
                    )
                    break # Found a compatible specifier, no need to check further in the list
            except InvalidSpecifier as e:
                msg = f"Malformed ILR version specifier string '{version_specifier_str}' in 'ilr_versions_supported' for plugin '{plugin_id}': {e}"
                self._add_version_error("ILR_SPECIFIER_INVALID_SYNTAX", msg, plugin_id) # Changed error code for clarity
                has_specifier_errors = True
                # Continue checking other specifiers in case one is valid and compatible
    
        if found_compatible_version:
            # If a compatible specifier was found, the plugin is compatible.
            # We might still have logged errors for other malformed specifiers in the list.
            # The current design of returning self.errors means those parse errors will be reported.
            # This seems reasonable: the plugin is compatible, but its manifest has some malformed specifiers.
            # For strict compatibility success (no errors at all), one might clear self.errors here.
            # However, retaining them provides more info. Let's keep them for now.
            # The method returns (True, list_of_errors_including_parse_errors_of_other_specifiers_if_any)
            return True, list(self.errors) # Return current errors which might include specifier parse errors

        # If no compatible version specifier was found
        # If has_specifier_errors is True, specific errors about malformed specifiers have already been added.
        # If all specifiers were syntactically valid but none matched, add a general incompatibility error.
        if not self.errors: # Only add general incompatibility if no specific parse/syntax errors were already added
            msg = (
                f"Plugin '{plugin_id}' requires ILR versions compatible with any of {supported_versions_list}, "
                f"but Core ILR version {core_ilr_version_str} does not satisfy any of these."
            )
            self._add_version_error("ILR_VERSION_NO_MATCH", msg, plugin_id)
    
        return False, list(self.errors)
