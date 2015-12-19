<!-- Tufts VUE 3.2.2 concept-map (simple2neurons.vue) 2015-12-15 -->
<!-- Tufts VUE: http://vue.tufts.edu/ -->
<!-- Do Not Remove: VUE mapping @version(1.1) jar:file:/opt/vue/VUE.jar!/tufts/vue/resources/lw_mapping_1_1.xml -->
<!-- Do Not Remove: Saved date Tue Dec 15 12:46:06 CET 2015 by nicolo on platform Linux 4.3.1-040301-generic in JVM 1.8.0_66-b17 -->
<!-- Do Not Remove: Saving version @(#)VUE: built May 23 2013 at 2146 by tomadm on Linux 2.6.18-348.2.1.el5 i386 JVM 1.7.0_21-b11(bits=32) -->
<?xml version="1.0" encoding="US-ASCII"?>
<LW-MAP xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="none" ID="0"
    label="simple2neurons.vue" created="0" x="0.0" y="0.0"
    width="1.4E-45" height="1.4E-45" strokeWidth="0.0" autoSized="false">
    <resource referenceCreated="1450179966305" size="11478"
        spec="/home/nicolo/Git/pyNeMo/nets/simple2neurons.vue" type="1" xsi:type="URLResource">
        <title>simple2neurons.vue</title>
        <property key="File" value="/home/nicolo/Git/pyNeMo/nets/simple2neurons.vue"/>
    </resource>
    <fillColor>#FFFFFF</fillColor>
    <strokeColor>#404040</strokeColor>
    <textColor>#000000</textColor>
    <font>SansSerif-plain-14</font>
    <URIString>http://vue.tufts.edu/rdf/resource/6832c7827f0001013ad55cd60b0f4a2b</URIString>
    <child ID="225" label="TonicBurstingTesting" layerID="13"
        created="1449248497821" x="534.9225" y="-43.418037"
        width="128.0" height="23.0" strokeWidth="1.0" autoSized="true" xsi:type="node">
        <fillColor>#F2AE45</fillColor>
        <strokeColor>#776D6D</strokeColor>
        <textColor>#000000</textColor>
        <font>Arial-plain-12</font>
        <URIString>http://vue.tufts.edu/rdf/resource/6df153917f000101173546659a7d7a90</URIString>
        <shape arcwidth="20.0" archeight="20.0" xsi:type="roundRect"/>
    </child>
    <child ID="228" label="TonicBurstingTesting" layerID="13"
        created="1449311316379" x="781.09106" y="-43.418037"
        width="128.0" height="23.0" strokeWidth="1.0" autoSized="true" xsi:type="node">
        <fillColor>#F2AE45</fillColor>
        <strokeColor>#776D6D</strokeColor>
        <textColor>#000000</textColor>
        <font>Arial-plain-12</font>
        <URIString>http://vue.tufts.edu/rdf/resource/71b14e3a7f00010177d3fc36c5745fc2</URIString>
        <shape arcwidth="20.0" archeight="20.0" xsi:type="roundRect"/>
    </child>
    <child ID="229" label="InhMedium" layerID="13"
        created="1449311334635" x="609.5388" y="-20.91803"
        width="202.0628" height="33.13109" strokeWidth="1.0"
        autoSized="false" controlCount="1" arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/71b14e3b7f00010177d3fc363ade4442</URIString>
        <point1 x="610.0388" y="-20.41803"/>
        <point2 x="811.1016" y="-20.41803"/>
        <ID1 xsi:type="node">225</ID1>
        <ID2 xsi:type="node">228</ID2>
        <ctrlPoint0 x="659.59106" y="30.844147" xsi:type="point"/>
    </child>
    <child ID="230" label="InhStrongSlow" layerID="13"
        created="1449311387773" x="607.1144" y="-86.78694"
        width="213.56213" height="43.86891" strokeWidth="1.0"
        autoSized="false" controlCount="1" arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/71b14e3d7f00010177d3fc36a62cf332</URIString>
        <point1 x="820.1765" y="-43.41803"/>
        <point2 x="607.6144" y="-43.41803"/>
        <ID1 xsi:type="node">228</ID1>
        <ID2 xsi:type="node">225</ID2>
        <ctrlPoint0 x="662.59106" y="-116.15585" xsi:type="point"/>
    </child>
    <child ID="252" label="&quot;/doublePendulumGazebo/body&quot;, 1"
        layerID="13" created="1449948270675" x="1070.0729"
        y="-363.24124" width="333.02023" height="102.8"
        strokeWidth="1.0" autoSized="false" xsi:type="node">
        <fillColor>#F2AE45</fillColor>
        <strokeColor>#776D6D</strokeColor>
        <textColor>#000000</textColor>
        <font>Arial-plain-12</font>
        <URIString>http://vue.tufts.edu/rdf/resource/97a6feb47f000101321d3313ed5943e4</URIString>
        <shape xsi:type="chevron"/>
    </child>
    <child ID="254" label="Spike" layerID="13" created="1449948276806"
        x="624.61926" y="-260.94125" width="495.37537"
        height="218.02322" strokeWidth="1.0" autoSized="false"
        controlCount="0" arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/97a6feb67f000101321d331391ee01c8</URIString>
        <point1 x="625.11926" y="-43.41803"/>
        <point2 x="1119.4946" y="-260.44125"/>
        <ID1 xsi:type="node">225</ID1>
        <ID2 xsi:type="node">252</ID2>
    </child>
    <child ID="255" label="Spike" layerID="13" created="1449948279946"
        x="860.67456" y="-260.94122" width="304.5219" height="218.0232"
        strokeWidth="1.0" autoSized="false" controlCount="0"
        arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/97a6feb77f000101321d3313800fe53c</URIString>
        <point1 x="861.1746" y="-43.41803"/>
        <point2 x="1164.6965" y="-260.44122"/>
        <ID1 xsi:type="node">228</ID1>
        <ID2 xsi:type="node">252</ID2>
    </child>
    <child ID="274"
        label="_stim_a = 20&#xa;_stim_b = 5&#xa;_stim_lenght = 10&#xa;_stim_distance = 100"
        layerID="13" created="1450118219835" x="1181.9021" y="-148.4411"
        width="182.5" height="115.5" strokeWidth="1.0" autoSized="true" xsi:type="node">
        <fillColor>#FEFD8C</fillColor>
        <strokeColor>#776D6D</strokeColor>
        <textColor>#000000</textColor>
        <font>Arial-plain-12</font>
        <URIString>http://vue.tufts.edu/rdf/resource/a1c817627f000101143e6c1e69286b42</URIString>
        <shape xsi:type="rhombus"/>
    </child>
    <child ID="281" label="_stim_a, 0, 5000" layerID="13"
        created="1450179814413" x="524.5868" y="-268.61816"
        width="103.0" height="23.0" strokeWidth="1.0" autoSized="true" xsi:type="node">
        <fillColor>#F2AE45</fillColor>
        <strokeColor>#776D6D</strokeColor>
        <textColor>#000000</textColor>
        <font>Arial-plain-12</font>
        <URIString>http://vue.tufts.edu/rdf/resource/a575fc027f00010146daa8018b39e48a</URIString>
        <shape xsi:type="rectangle"/>
    </child>
    <child ID="282" layerID="13" created="1450179948390" x="576.7529"
        y="-246.11816" width="21.503418" height="203.1997"
        strokeWidth="1.0" autoSized="false" controlCount="0"
        arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/a575fc037f00010146daa801e5e0cc8b</URIString>
        <point1 x="577.2529" y="-245.61816"/>
        <point2 x="597.75635" y="-43.418457"/>
        <ID1 xsi:type="node">281</ID1>
        <ID2 xsi:type="node">225</ID2>
    </child>
    <child ID="283" layerID="13" created="1450179950243" x="589.3237"
        y="-246.11816" width="242.53046" height="203.20013"
        strokeWidth="1.0" autoSized="false" controlCount="0"
        arrowState="2" xsi:type="link">
        <strokeColor>#404040</strokeColor>
        <textColor>#404040</textColor>
        <font>Arial-plain-11</font>
        <URIString>http://vue.tufts.edu/rdf/resource/a575fc047f00010146daa801077e08c7</URIString>
        <point1 x="589.8237" y="-245.61816"/>
        <point2 x="831.3542" y="-43.41803"/>
        <ID1 xsi:type="node">281</ID1>
        <ID2 xsi:type="node">228</ID2>
    </child>
    <layer ID="13" label="Layer 1" created="1449152123076" x="0.0"
        y="0.0" width="1.4E-45" height="1.4E-45" strokeWidth="0.0" autoSized="false">
        <URIString>http://vue.tufts.edu/rdf/resource/6832c78d7f0001013ad55cd620b39e7c</URIString>
    </layer>
    <userZoom>0.9283209568865544</userZoom>
    <userOrigin x="298.21112" y="-669.5952"/>
    <presentationBackground>#202020</presentationBackground>
    <PathwayList currentPathway="0" revealerIndex="-1">
        <pathway ID="0" label="Percorso senza titolo" created="0"
            x="0.0" y="0.0" width="1.4E-45" height="1.4E-45"
            strokeWidth="0.0" autoSized="false" currentIndex="0" open="true">
            <strokeColor>#B3993333</strokeColor>
            <textColor>#000000</textColor>
            <font>SansSerif-plain-14</font>
            <URIString>http://vue.tufts.edu/rdf/resource/6832c7907f0001013ad55cd659ef53a5</URIString>
            <masterSlide ID="14" created="1449152123136" x="0.0" y="0.0"
                width="800.0" height="600.0" locked="true"
                strokeWidth="0.0" autoSized="false">
                <fillColor>#000000</fillColor>
                <strokeColor>#404040</strokeColor>
                <textColor>#000000</textColor>
                <font>SansSerif-plain-14</font>
                <URIString>http://vue.tufts.edu/rdf/resource/6832c7907f0001013ad55cd685f955ab</URIString>
                <titleStyle ID="15" label="Header"
                    created="1449152123148" x="329.0" y="174.5"
                    width="142.0" height="51.0" strokeWidth="0.0"
                    autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#FFFFFF</textColor>
                    <font>Gill Sans-plain-36</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/6832c7917f0001013ad55cd613b1ccae</URIString>
                    <shape xsi:type="rectangle"/>
                </titleStyle>
                <textStyle ID="16" label="Slide Text"
                    created="1449152123150" x="340.0" y="282.5"
                    width="120.0" height="35.0" strokeWidth="0.0"
                    autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#FFFFFF</textColor>
                    <font>Gill Sans-plain-22</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/6832c7917f0001013ad55cd64517407a</URIString>
                    <shape xsi:type="rectangle"/>
                </textStyle>
                <linkStyle ID="17" label="Links" created="1449152123151"
                    x="372.5" y="385.0" width="55.0" height="30.0"
                    strokeWidth="0.0" autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#B3BFE3</textColor>
                    <font>Gill Sans-plain-18</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/6832c7927f0001013ad55cd6b0dd994f</URIString>
                    <shape xsi:type="rectangle"/>
                </linkStyle>
            </masterSlide>
        </pathway>
    </PathwayList>
    <date>2015-12-02</date>
    <modelVersion>6</modelVersion>
    <saveLocation>/home/nicolo/Git/pyNeMo/nets</saveLocation>
    <saveFile>/home/nicolo/Git/pyNeMo/nets/simple2neurons.vue</saveFile>
</LW-MAP>
