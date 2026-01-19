from neo4j import GraphDatabase
#interface.py mrugankthatte
class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            session.run("CALL gds.graph.drop('prGraph', false) YIELD graphName")

            session.run(f"""
                CALL gds.graph.project(
                    'prGraph',
                    'Location',
                    {{
                        TRIP: {{
                            properties: ['{weight_property}']
                        }}
                    }}
                )
            """)

            result = session.run(f"""
                CALL gds.pageRank.stream('prGraph', {{
                    maxIterations: {max_iterations},
                    relationshipWeightProperty: '{weight_property}'
                }})
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC
            """)

            nodes = [(record["name"], record["score"]) for record in result]
            return nodes[0], nodes[-1]

    def bfs(self, start_node, last_node):
        with self._driver.session() as session:
            session.run("CALL gds.graph.drop('bfsGraph', false) YIELD graphName")

            session.run("""
                CALL gds.graph.project(
                    'bfsGraph',
                    'Location',
                    'TRIP'
                )
            """)

            source_id = session.run(f"""
                MATCH (n:Location {{name: {start_node}}})
                RETURN id(n) AS id
            """).single()["id"]

            target_id = session.run(f"""
                MATCH (n:Location {{name: {last_node}}})
                RETURN id(n) AS id
            """).single()["id"]

            
            result = session.run(f"""
                CALL gds.beta.bfs.stream('bfsGraph', {{
                    sourceNode: {source_id},
                    targetNodes: [{target_id}],
                    maxDepth: 10
                }})
                YIELD targetNode
                RETURN gds.util.asNode(targetNode).name AS reachable
            """)

            return [record["reachable"] for record in result]