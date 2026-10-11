# Translations

Home Assistant blueprints use literal `name` and `description` strings from the
YAML file, as described in the official
[blueprint schema](https://www.home-assistant.io/docs/blueprint/schema/). They
do not currently work like custom integrations with automatic translation files.

The blueprint itself is therefore published as three files with identical logic:
Polish (`smart_irrigation.yaml`, the source), English (`smart_irrigation_en.yaml`)
and German (`smart_irrigation_de.yaml`). The English and German files are
generated from the Polish source with `tools/blueprint_i18n.py` and the catalog
`i18n/smart_irrigation.yaml`. The guides below translate the labels of the
Polish blueprint for users of other languages.

Available translations:

- [English](en.md)
- [Deutsch](de.md)
- [Español](es.md)
- [Français](fr.md)
- [Italiano](it.md)
- [Nederlands](nl.md)
- [Português](pt-BR.md)
