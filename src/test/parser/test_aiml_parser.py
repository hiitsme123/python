import unittest
import os
from xml.etree.ElementTree import ParseError

from programy.parser.aiml_parser import AIMLParser
from programy.parser.exceptions import ParserException
from programy.parser.pattern.nodes.root import PatternRootNode
from programy.parser.pattern.nodes.topic import PatternTopicNode
from programy.parser.pattern.nodes.that import PatternThatNode
from programy.parser.pattern.nodes.word import PatternWordNode
from programy.parser.pattern.nodes.oneormore import PatternOneOrMoreWildCardNode
from programy.parser.pattern.nodes.template import PatternTemplateNode

from programy.dialog import Sentence

class AIMLParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = AIMLParser(supress_warnings=True, stop_on_invalid=True)
        self.assertIsNotNone(self.parser)

    def test_parse_from_file_valid(self):
        filename = os.path.dirname(__file__)+ '/valid.aiml'
        self.parser.parse_from_file(filename)

    def test_parse_from_file_invalid(self):
        filename = os.path.dirname(__file__)+ '/invalid.aiml'
        self.parser.parse_from_file(filename)

    def test_crud(self):
        with self.assertRaises(ParseError) as raised:
            self.parser.parse_from_text(
                """Blah Blah Blah
                """)

    def test_no_aiml(self):
        with self.assertRaises(ParseError) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                """)
        self.assertTrue(str(raised.exception).startswith("no element found:"))

    def test_no_content(self):
        with self.assertRaises(ParseError) as raised:
            self.parser.parse_from_text(
                """
                """)
        self.assertTrue(str(raised.exception).startswith("no element found:"))

    def test_base_aiml_no_content(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no categories in aiml file")

    def test_base_aiml_topic_no_name(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, missing name attribute for topic")

    def test_base_aiml_topic_no_category(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="test">
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no categories in topic")

    def test_base_aiml_topic_category_no_content(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="test">
                        <category>
                        </category>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no template node found in category")

    def test_base_aiml_topic_at_multiple_levels(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="test">
                        <category>
                            <topic name="test2" />
                            <pattern>*</pattern>
                            <template>RESPONSE</template>
                        </category>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, topic exists in category AND as parent node")

    def test_base_aiml_topic_category_no_template(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="test">
                        <category>
                            <pattern>*</pattern>
                        </category>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no template node found in category")

    def test_base_aiml_category_no_content(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <category>
                    </category>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no template node found in category")

    def test_base_aiml_category_no_template(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <category>
                        <pattern>*</pattern>
                    </category>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error, no template node found in category")

    def test_base_aiml_topic_empty_parent_node(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="">
                        <category>
                            <pattern>*</pattern>
                            <template>RESPONSE</template>
                        </category>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Topic name empty or null")

    def test_base_aiml_topic_with_something_else(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <topic name="test">
                        <xxxx>
                            <pattern>*</pattern>
                            <template>RESPONSE</template>
                        </xxxx>
                    </topic>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Error unknown child node of topic, xxxx")

    def test_base_aiml_topic_empty_child_node1(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <category>
                        <topic name="" />
                        <pattern>*</pattern>
                        <template>RESPONSE</template>
                    </category>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Topic node text is empty")

    def test_base_aiml_topic_empty_child_node2(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <category>
                        <topic></topic>
                        <pattern>*</pattern>
                        <template>RESPONSE</template>
                    </category>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "Topic node text is empty")

    def test_base_aiml_that_empty_child_node(self):
        with self.assertRaises(ParserException) as raised:
            self.parser.parse_from_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <aiml>
                    <category>
                        <that></that>
                        <pattern>*</pattern>
                        <template>RESPONSE</template>
                    </category>
                </aiml>
                """)
        self.assertEqual(raised.exception.message, "That node text is empty")

    def test_base_aiml_topic_category_template(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <topic name="test">
                    <category>
                        <pattern>*</pattern>
                        <template>RESPONSE</template>
                    </category>
                </topic>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        template = that.star.template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE")

    def test_base_aiml_topic_category_template_multi_line(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <topic name="test">
                    <category>
                        <pattern>*</pattern>
                        <template>
                            RESPONSE1,
                            RESPONSE2.
                            RESPONSE3
                        </template>
                    </category>
                </topic>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        template = that.star.template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE1, RESPONSE2. RESPONSE3")

    def test_base_aiml_category_template(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>*</pattern>
                    <template>RESPONSE</template>
                </category>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        template = that.star.template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE")

    def test_base_aiml_category_template_that(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>*</pattern>
                    <that>something</that>
                    <template>RESPONSE</template>
                </category>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertEqual(len(that.children), 1)
        self.assertIsNotNone(that.children[0])
        self.assertIsInstance(that.children[0], PatternWordNode)
        self.assertEqual(that.children[0].word, "something")

        template = that.children[0].template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE")

    def test_base_aiml_category_template_topic(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>*</pattern>
                    <topic>something</topic>
                    <template>RESPONSE</template>
                </category>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "something")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        template = that.star.template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE")

    def test_base_aiml_category_template_topic_that(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>*</pattern>
                    <that>something</that>
                    <topic>other</topic>
                    <template>RESPONSE</template>
                </category>
            </aiml>
            """)

        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertTrue(self.parser.pattern_parser.root.has_one_or_more())

        node = self.parser.pattern_parser.root.star
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternOneOrMoreWildCardNode)
        self.assertEquals(node.wildcard, "*")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "other")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertEqual(len(that.children), 1)
        self.assertIsNotNone(that.children[0])
        self.assertIsInstance(that.children[0], PatternWordNode)
        self.assertEqual(that.children[0].word, "something")

        template = that.children[0].template
        self.assertIsNotNone(template)
        self.assertIsInstance(template, PatternTemplateNode)
        self.assertEqual(template.template.resolve(bot=None, clientid="test"), "RESPONSE")

    def test_base_aiml_multiple_categories(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>Hello</pattern>
                    <template>Hiya</template>
                </category>
                <category>
                    <pattern>Goodbye</pattern>
                    <template>See ya</template>
                </category>
            </aiml>
            """)
        self.assertIsNotNone(self.parser.pattern_parser)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertIsInstance(self.parser.pattern_parser.root, PatternRootNode)
        self.assertEqual(2, len(self.parser.pattern_parser.root.children))

        node = self.parser.pattern_parser.root.children[1]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternWordNode)
        self.assertEquals(node.word, "Hello")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        node = self.parser.pattern_parser.root.children[0]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternWordNode)
        self.assertEquals(node.word, "Goodbye")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

    def test_base_aiml_multiple_categories_in_a_topic(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <topic name="test">
                    <category>
                        <pattern>Hello</pattern>
                        <template>Hiya</template>
                    </category>
                    <category>
                        <pattern>Goodbye</pattern>
                        <template>See ya</template>
                    </category>
                </topic>
            </aiml>
            """)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertEqual(2, len(self.parser.pattern_parser.root.children))

        node = self.parser.pattern_parser.root.children[1]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternWordNode)
        self.assertEquals(node.word, "Hello")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        node = self.parser.pattern_parser.root.children[0]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, PatternWordNode)
        self.assertEquals(node.word, "Goodbye")

        topic = node.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

    def test_base_aiml_multiple_categories_in_and_out_of_topic(self):
        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>Welcome</pattern>
                    <template>Hello there</template>
                </category>
                <topic name="test">
                    <category>
                        <pattern>Hello</pattern>
                        <template>Hiya</template>
                    </category>
                    <category>
                        <pattern>Goodbye</pattern>
                        <template>See ya</template>
                    </category>
                </topic>
                <category>
                    <pattern>Interesting</pattern>
                    <template>Yes</template>
                </category>
            </aiml>
            """)
        self.assertIsNotNone(self.parser.pattern_parser.root)
        self.assertEqual(4, len(self.parser.pattern_parser.root.children))

        node1 = self.parser.pattern_parser.root.children[0]
        self.assertIsNotNone(node1)
        self.assertIsInstance(node1, PatternWordNode)
        self.assertEquals(node1.word, "Interesting")

        topic = node1.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        node2 = self.parser.pattern_parser.root.children[1]
        self.assertIsNotNone(node2)
        self.assertIsInstance(node2, PatternWordNode)
        self.assertEquals(node2.word, "Goodbye")

        topic = node2.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        node3 = self.parser.pattern_parser.root.children[2]
        self.assertIsNotNone(node3)
        self.assertIsInstance(node3, PatternWordNode)
        self.assertEquals(node3.word, "Hello")

        topic = node3.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertEqual(len(topic.children), 1)
        self.assertIsNotNone(topic.children[0])
        self.assertIsInstance(topic.children[0], PatternWordNode)
        self.assertEqual(topic.children[0].word, "test")

        that = topic.children[0].that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

        node4 = self.parser.pattern_parser.root.children[3]
        self.assertIsNotNone(node4)
        self.assertIsInstance(node4, PatternWordNode)
        self.assertEquals(node4.word, "Welcome")

        topic = node4.topic
        self.assertIsNotNone(topic)
        self.assertIsInstance(topic, PatternTopicNode)
        self.assertTrue(topic.has_one_or_more())
        self.assertIsInstance(topic.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(topic.star.wildcard, "*")

        that = topic.star.that
        self.assertIsNotNone(that)
        self.assertIsInstance(that, PatternThatNode)
        self.assertTrue(that.has_one_or_more())
        self.assertIsInstance(that.star, PatternOneOrMoreWildCardNode)
        self.assertEquals(that.star.wildcard, "*")

    def test_match_sentence(self):

        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>HELLO</pattern>
                    <template>Hiya</template>
                </category>
            </aiml>
            """)

        self.parser.pattern_parser.dump()

        context = self.parser.match_sentence(None, "test", Sentence("HELLO"), "*", "*")
        self.assertIsNotNone(context)
        self.assertEqual("Hiya", context.template_node().template.resolve(None, None))

    def test_inline_br_html(self):

        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>HELLO</pattern>
                    <template>Hello  <br/> World</template>
                </category>
            </aiml>
            """)

        self.parser.pattern_parser.dump(output_func=print)

    def test_inline_bold_html(self):

        self.parser.parse_from_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <aiml>
                <category>
                    <pattern>HELLO</pattern>
                    <template>Hello <bold>You</bold> World</template>
                </category>
            </aiml>
            """)

        self.parser.pattern_parser.dump(output_func=print)


if __name__ == '__main__':
    unittest.main()
