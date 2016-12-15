#
# This module builds upon Cycles nodes work licensed as
# Copyright 2011-2013 Blender Foundation
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import armutils
import material.make_texture as make_texture
import material.mat_state as state

str_tex_checker = """vec3 tex_checker(const vec3 co, const vec3 col1, const vec3 col2, const float scale) {
    vec3 p = co * scale;
    // Prevent precision issues on unit coordinates
    //p.x = (p.x + 0.000001) * 0.999999;
    //p.y = (p.y + 0.000001) * 0.999999;
    //p.z = (p.z + 0.000001) * 0.999999;
    float xi = abs(floor(p.x));
    float yi = abs(floor(p.y));
    float zi = abs(floor(p.z));
    bool check = ((mod(xi, 2.0) == mod(yi, 2.0)) == bool(mod(zi, 2.0)));
    return check ? col1 : col2;
}
"""

# Created by inigo quilez - iq/2013
# License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
str_tex_voronoi = """//vec3 hash(vec3 x) {
    //return texture(snoise, (x.xy + vec2(3.0, 1.0) * x.z + 0.5) / 64.0, -100.0).xyz;
    //x = vec3(dot(x, vec3(127.1, 311.7, 74.7)),
    //         dot(x, vec3(269.5, 183.3, 246.1)),
    //         dot(x, vec3(113.5, 271.9, 124.6)));
    //return fract(sin(x) * 43758.5453123);
//}
vec4 tex_voronoi(const vec3 x) {
    vec3 xx = x / 3.0; // Match cycles
    vec3 p = floor(xx);
    vec3 f = fract(xx);
    float id = 0.0;
    float res = 100.0;
    for (int k = -1; k <= 1; k++)
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec3 b = vec3(float(i), float(j), float(k));
        vec3 pb = p + b;
        vec3 r = vec3(b) - f + texture(snoise, (pb.xy + vec2(3.0, 1.0) * pb.z + 0.5) / 64.0, -100.0).xyz;
        //vec3 r = vec3(b) - f + hash(p + b);
        float d = dot(r, r);
        if (d < res) {
            id = dot(p + b, vec3(1.0, 57.0, 113.0));
            res = d;
        }
    }
    vec3 col = 0.5 + 0.5 * cos(id * 0.35 + vec3(0.0, 1.0, 2.0));
    return vec4(col, sqrt(res));
}
"""

# str_tex_noise = """
# float tex_noise_f(const vec3 x) {
#     vec3 p = floor(x);
#     vec3 f = fract(x);
#     f = f * f * (3.0 - 2.0 * f);
#     vec2 uv = (p.xy + vec2(37.0, 17.0) * p.z) + f.xy;
#     vec2 rg = texture(snoisea, (uv + 0.5) / 64.0, -100.0).yx;
#     return mix(rg.x, rg.y, f.z);
# }
# float tex_noise(vec3 q) {
#     //return fract(sin(dot(q.xy, vec2(12.9898,78.233))) * 43758.5453);
#     q *= 2.0; // Match to Cycles
#     const mat3 m = mat3(0.00, 0.80, 0.60, -0.80, 0.36, -0.48, -0.60, -0.48, 0.64);
#     float f = 0.5000 * tex_noise_f(q); q = m * q * 2.01;
#     f += 0.2500 * tex_noise_f(q); q = m * q * 2.02;
#     f += 0.1250 * tex_noise_f(q); q = m * q * 2.03;
#     f += 0.0625 * tex_noise_f(q); q = m * q * 2.01;
#     return pow(f, 3.0);
# }
# """
# Created by Nikita Miropolskiy, nikat/2013
# Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
str_tex_noise = """
vec3 random3(vec3 c) {
    // Might not be precise on lowp floats
    float j = 4096.0 * sin(dot(c, vec3(17.0, 59.4, 15.0)));
    vec3 r;
    r.z = fract(512.0 * j);
    j *= 0.125;
    r.x = fract(512.0 * j);
    j *= 0.125;
    r.y = fract(512.0 * j);
    return r - 0.5;
}
float tex_noise_f(vec3 p) {
    const float F3 = 0.3333333;
    const float G3 = 0.1666667;
    vec3 s = floor(p + dot(p, vec3(F3)));
    vec3 x = p - s + dot(s, vec3(G3));
    vec3 e = step(vec3(0.0), x - x.yzx);
    vec3 i1 = e*(1.0 - e.zxy);
    vec3 i2 = 1.0 - e.zxy*(1.0 - e);
    vec3 x1 = x - i1 + G3;
    vec3 x2 = x - i2 + 2.0*G3;
    vec3 x3 = x - 1.0 + 3.0*G3;
    vec4 w, d;
    w.x = dot(x, x);
    w.y = dot(x1, x1);
    w.z = dot(x2, x2);
    w.w = dot(x3, x3);
    w = max(0.6 - w, 0.0);
    d.x = dot(random3(s), x);
    d.y = dot(random3(s + i1), x1);
    d.z = dot(random3(s + i2), x2);
    d.w = dot(random3(s + 1.0), x3);
    w *= w;
    w *= w;
    d *= w;
    return clamp(dot(d, vec4(52.0)), 0.0, 1.0);
}
float tex_noise(vec3 p) {
    return 0.5333333 * tex_noise_f(p)
        + 0.2666667 * tex_noise_f(2.0 * p)
        + 0.1333333 * tex_noise_f(4.0 * p)
        + 0.0666667 * tex_noise_f(8.0 * p);
}
"""

def parse(nodes, vert, frag):
    output_node = node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node != None:
        parse_output(output_node, vert, frag)

def parse_output(node, _vert, _frag):
    global parsed
    global parents
    global normal_written # Normal socket is linked on shader node - overwrite fs normal
    global vert
    global frag
    global str_tex_checker
    global str_tex_voronoi
    parsed = [] # Compute nodes only once
    parents = []
    normal_written = False
    vert = _vert
    frag = _frag
    out_basecol, out_roughness, out_metallic, out_occlusion = parse_shader_input(node.inputs[0])
    frag.write('basecol = {0};'.format(out_basecol))
    frag.write('roughness = {0};'.format(out_roughness))
    frag.write('metallic = {0};'.format(out_metallic))
    frag.write('occlusion = {0};'.format(out_occlusion))

def parse_group(node, socket): # Entering group
    index = socket_index(node, socket)
    output_node = node_by_type(node.node_tree.nodes, 'GROUP_OUTPUT')
    if output_node == None:
        return
    inp = output_node.inputs[index]
    parents.append(node)
    out_group = parse_input(inp)
    parents.pop()
    return out_group

def parse_input_group(node, socket): # Leaving group
    index = socket_index(node, socket)
    parent = parents[-1]
    inp = parent.inputs[index]
    return parse_input(inp)

def parse_input(inp):
    if inp.type == 'SHADER':
        return parse_shader_input(inp)
    elif inp.type == 'RGB':
        return parse_vector_input(inp)
    elif inp.type == 'RGBA':
        return parse_vector_input(inp)
    elif inp.type == 'VECTOR':
        return parse_vector_input(inp)
    elif inp.type == 'VALUE':
        return parse_value_input(inp)

def parse_shader_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_shader_input(l.from_node.inputs[0])

        return parse_shader(l.from_node, l.from_socket)
    else:
        out_basecol = 'vec3(0.8)'
        out_roughness = '0.0'
        out_metallic = '0.0'
        out_occlusion = '1.0'
        return out_basecol, out_roughness, out_metallic, out_occlusion

def write_normal(inp):
    if inp.is_linked:
        frag.write('n = {0};'.format(parse_vector_input(inp)))
        normal_written = True

def parse_shader(node, socket):   
    out_basecol = 'vec3(0.8)'
    out_roughness = '0.0'
    out_metallic = '0.0'
    out_occlusion = '1.0'

    if node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            pass
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'MIX_SHADER':
        fac = parse_value_input(node.inputs[0])
        fac_var = node_name(node.name) + '_fac'
        fac_inv_var = node_name(node.name) + '_fac_inv'
        frag.write('float {0} = {1};'.format(fac_var, fac))
        frag.write('float {0} = 1.0 - {1};'.format(fac_inv_var, fac_var))
        bc1, rough1, met1, occ1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2, occ2 = parse_shader_input(node.inputs[2])
        out_basecol = '({0} * {3} + {1} * {2})'.format(bc1, bc2, fac_var, fac_inv_var)
        out_roughness = '({0} * {3} + {1} * {2})'.format(rough1, rough2, fac_var, fac_inv_var)
        out_metallic = '({0} * {3} + {1} * {2})'.format(met1, met2, fac_var, fac_inv_var)
        out_occlusion = '({0} * {3} + {1} * {2})'.format(occ1, occ2, fac_var, fac_inv_var)

    elif node.type == 'ADD_SHADER':
        bc1, rough1, met1, occ1 = parse_shader_input(node.inputs[0])
        bc2, rough2, met2, occ2 = parse_shader_input(node.inputs[1])
        out_basecol = '({0} + {1})'.format(bc1, bc2)
        out_roughness = '({0} + {1})'.format(rough1, rough2)
        out_metallic = '({0} + {1})'.format(met1, met2)
        out_occlusion = '({0} + {1})'.format(occ1, occ2)

    elif node.type == 'BSDF_DIFFUSE':
        write_normal(node.inputs[2])
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])

    elif node.type == 'BSDF_GLOSSY':
        write_normal(node.inputs[2])
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '1.0'

    elif node.type == 'AMBIENT_OCCLUSION':
        # Single channel
        out_occlusion = parse_vector_input(node.inputs[0]) + '.r'

    elif node.type == 'BSDF_ANISOTROPIC':
        write_normal(node.inputs[4])
        # Revert to glossy
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '1.0'

    elif node.type == 'EMISSION':
        # Multiply basecol
        out_basecol = parse_vector_input(node.inputs[0])
        strength = parse_value_input(node.inputs[1])
        out_basecol = '({0} * {1} * 50.0)'.format(out_basecol, strength)

    elif node.type == 'BSDF_GLASS':
        # write_normal(node.inputs[3])
        # Switch to translucent
        pass

    elif node.type == 'BSDF_HAIR':
        pass

    elif node.type == 'HOLDOUT':
        # Occlude
        out_occlusion = '0.0'

    elif node.type == 'BSDF_REFRACTION':
        # write_normal(node.inputs[3])
        pass

    elif node.type == 'SUBSURFACE_SCATTERING':
        # write_normal(node.inputs[4])
        pass

    elif node.type == 'BSDF_TOON':
        # write_normal(node.inputs[3])
        pass

    elif node.type == 'BSDF_TRANSLUCENT':
        # write_normal(node.inputs[1])
        pass

    elif node.type == 'BSDF_TRANSPARENT':
        pass

    elif node.type == 'BSDF_VELVET':
        write_normal(node.inputs[2])
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = '1.0'
        out_metallic = '1.0'

    elif node.type == 'VOLUME_ABSORPTION':
        pass

    elif node.type == 'VOLUME_SCATTER':
        pass

    return out_basecol, out_roughness, out_metallic, out_occlusion

def write_result(l):
    res_var = node_name(l.from_node.name) + '_' + socket_name(l.from_socket.name) + '_res'
    st = l.from_socket.type
    if res_var not in parsed:
        parsed.append(res_var)
        if st == 'RGB' or st == 'RGBA':
            res = parse_rgb(l.from_node, l.from_socket)
            frag.write('vec3 {0} = {1};'.format(res_var, res))
        elif st == 'VECTOR':
            res = parse_vector(l.from_node, l.from_socket)
            frag.write('vec3 {0} = {1};'.format(res_var, res))
        elif st == 'VALUE':
            res = parse_value(l.from_node, l.from_socket)
            frag.write('float {0} = {1};'.format(res_var, res))
    return res_var

def parse_vector_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_vector_input(l.from_node.inputs[0])

        res_var = write_result(l)
        st = l.from_socket.type        
        if st == 'RGB' or st == 'RGBA' or st == 'VECTOR':
            return res_var
        else: # VALUE
            return 'vec3({0})'.format(res_var)
    else:
        if inp.type == 'VALUE': # Unlinked reroute
            return tovec3([0.0, 0.0, 0.0])
        else:
            return tovec3(inp.default_value)

def parse_rgb(node, socket):

    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Vcols
        pass

    elif node.type == 'RGB':
        return tovec3(socket.default_value)

    elif node.type == 'TEX_BRICK':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_CHECKER':
        frag.add_function(str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        return 'tex_checker({0}, {1}, {2}, {3})'.format(co, col1, col2, scale)

    elif node.type == 'TEX_ENVIRONMENT':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_GRADIENT':
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        grad = node.gradient_type
        if grad == 'LINEAR':
            f = '{0}.x'.format(co)
        elif grad == 'QUADRATIC':
            f = '0.0'
        elif grad == 'EASING':
            f = '0.0'
        elif grad == 'DIAGONAL':
            f = '({0}.x + {0}.y) * 0.5'.format(co)
        elif grad == 'RADIAL':
            f = 'atan({0}.y, {0}.x) / PI2 + 0.5'.format(co)
        elif grad == 'QUADRATIC_SPHERE':
            f = '0.0'
        elif grad == 'SPHERICAL':
            f = 'max(1.0 - sqrt({0}.x * {0}.x + {0}.y * {0}.y + {0}.z * {0}.z), 0.0)'.format(co)
        return 'vec3(clamp({0}, 0.0, 1.0))'.format(f)

    elif node.type == 'TEX_IMAGE':
        tex_name = armutils.safe_source_name(node.name)
        tex = make_texture.make_texture(node, tex_name)
        if tex != None:
            state.mat_context['bind_textures'].append(tex)
            state.data.add_elem('tex', 2)
            frag.add_uniform('sampler2D {0}'.format(tex_name))
            return 'texture({0}, texCoord).rgb'.format(tex_name)
        else:
            return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_MAGIC':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_MUSGRAVE':
        # Fall back to noise
        frag.add_function(str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'vec3(tex_noise_f({0} * {1}))'.format(co, scale)

    elif node.type == 'TEX_NOISE':
        frag.add_function(str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        # Slow..
        return 'vec3(tex_noise({0} * {1}), tex_noise({0} * {1} + vec3(0.33)), tex_noise({0} * {1} + vec3(0.66)))'.format(co, scale)

    elif node.type == 'TEX_POINTDENSITY':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_SKY':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_VORONOI':
        frag.add_function(str_tex_voronoi)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            return 'vec3(tex_voronoi({0} / {1}).a)'.format(co, scale)
        else: # CELLS
            return 'tex_voronoi({0} / {1}).rgb'.format(co, scale)

    elif node.type == 'TEX_WAVE':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'BRIGHTCONTRAST':
        out_col = parse_vector_input(node.inputs[0])
        bright = parse_value_input(node.inputs[1])
        contr = parse_value_input(node.inputs[2])
        frag.add_function(\
"""vec3 brightcontrast(const vec3 col, const float bright, const float contr) {
    float a = 1.0 + contr;
    float b = bright - contr * 0.5;
    return max(a * col + b, 0.0);
}
""")
        return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)

    elif node.type == 'GAMMA':
        out_col = parse_vector_input(node.inputs[0])
        gamma = parse_value_input(node.inputs[1])
        return 'pow({0}, vec3({1}))'.format(out_col, gamma)

    elif node.type == 'HUE_SAT':
#         hue = parse_value_input(node.inputs[0])
#         sat = parse_value_input(node.inputs[1])
#         val = parse_value_input(node.inputs[2])
#         fac = parse_value_input(node.inputs[3])
        out_col = parse_vector_input(node.inputs[4])
#         frag.add_function(\
# """vec3 hue_sat(const float hue, const float sat, const float val, const float fac, const vec3 col) {
# }
# """)
        return out_col

    elif node.type == 'INVERT':
        fac = parse_value_input(node.inputs[0])
        out_col = parse_vector_input(node.inputs[1])
        return 'mix({0}, vec3(1.0) - ({0}), {1})'.format(out_col, fac)

    elif node.type == 'MIX_RGB':
        fac = parse_value_input(node.inputs[0])
        fac_var = node_name(node.name) + '_fac'
        frag.write('float {0} = {1};'.format(fac_var, fac))
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        blend = node.blend_type
        if blend == 'MIX':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var)
        elif blend == 'ADD':
            out_col = 'mix({0}, {0} + {1}, {2})'.format(col1, col2, fac_var)
        elif blend == 'MULTIPLY':
            out_col = 'mix({0}, {0} * {1}, {2})'.format(col1, col2, fac_var)
        elif blend == 'SUBTRACT':
            out_col = 'mix({0}, {0} - {1}, {2})'.format(col1, col2, fac_var)
        elif blend == 'SCREEN':
            out_col = '(vec3(1.0) - (vec3(1.0 - {2}) + {2} * (vec3(1.0) - {1})) * (vec3(1.0) - {0}))'.format(col1, col2, fac_var)
        elif blend == 'DIVIDE':
            out_col = '(vec3((1.0 - {2}) * {0} + {2} * {0} / {1}))'.format(col1, col2, fac_var)
        elif blend == 'DIFFERENCE':
            out_col = 'mix({0}, abs({0} - {1}), {2})'.format(col1, col2, fac_var)
        elif blend == 'DARKEN':
            out_col = 'min({0}, {1} * {2})'.format(col1, col2, fac_var)
        elif blend == 'LIGHTEN':
            out_col = 'max({0}, {1} * {2})'.format(col1, col2, fac_var)
        elif blend == 'OVERLAY':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'DODGE':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'BURN':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'HUE':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'SATURATION':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'VALUE':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'COLOR':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        elif blend == 'SOFT_LIGHT':
            out_col = '((1.0 - {2}) * {0} + {2} * ((vec3(1.0) - {0}) * {1} * {0} + {0} * (vec3(1.0) - (vec3(1.0) - {1}) * (vec3(1.0) - {0}))));'.format(col1, col2, fac)
        elif blend == 'LINEAR_LIGHT':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
            # out_col = '({0} + {2} * (2.0 * ({1} - vec3(0.5))))'.format(col1, col2, fac_var)
        if node.use_clamp:
            return 'clamp({0}, vec3(0.0), vec3(1.0))'.format(out_col)
        else:
            return out_col

    elif node.type == 'CURVE_RGB':
        # Pass throuh
        return parse_vector_input(node.inputs[1])

    elif node.type == 'BLACKBODY':
        # Pass constant
        return tovec3([0.84, 0.38, 0.0])

    elif node.type == 'VALTORGB': # ColorRamp
        fac = parse_value_input(node.inputs[0])
        interp = node.color_ramp.interpolation
        elems = node.color_ramp.elements
        if len(elems) == 1:
            return tovec3(elems[0].color)
        if interp == 'CONSTANT':
            fac_var = node_name(node.name) + '_fac'
            frag.write('float {0} = {1};'.format(fac_var, fac))
            # Get index
            out_i = '0'
            for i in  range(1, len(elems)):
                out_i += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, elems[i].position)
            # Write cols array
            cols_var = node_name(node.name) + '_cols'
            frag.write('vec3 {0}[{1}];'.format(cols_var, len(elems)))
            for i in range(0, len(elems)):
                frag.write('{0}[{1}] = vec3({2}, {3}, {4});'.format(cols_var, i, elems[i].color[0], elems[i].color[1], elems[i].color[2]))
            return '{0}[{1}]'.format(cols_var, out_i)
        else: # Linear, .. - 2 elems only, end pos assumed to be 1
            # float f = clamp((pos - start) * (1.0 / (1.0 - start)), 0.0, 1.0);
            return 'mix({0}, {1}, clamp(({2} - {3}) * (1.0 / (1.0 - {3})), 0.0, 1.0))'.format(tovec3(elems[0].color), tovec3(elems[1].color), fac, elems[0].position)

    elif node.type == 'COMBHSV':
# vec3 hsv2rgb(vec3 c) {
#     vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
#     vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
#     return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
# }
# vec3 rgb2hsv(vec3 c) {
#     vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
#     vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
#     vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

#     float d = q.x - min(q.w, q.y);
#     float e = 1.0e-10;
#     return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
# }
        # Pass constant
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'COMBRGB':
        r = parse_value_input(node.inputs[0])
        g = parse_value_input(node.inputs[1])
        b = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(r, g, b)

    elif node.type == 'WAVELENGTH':
        # Pass constant
        return tovec3([0.0, 0.27, 0.19])

def parse_vector(node, socket):

    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Vector
        pass

    elif node.type == 'CAMERA':
        # View Vector
        return 'v'

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[0]: # Position
            return 'wposition'
        elif socket == node.outputs[1]: # Normal
            return 'n'
        elif socket == node.outputs[2]: # Tangent
            return 'vec3(0.0)'
        elif socket == node.outputs[3]: # True Normal
            return 'n'
        elif socket == node.outputs[4]: # Incoming
            return 'v'
        elif socket == node.outputs[5]: # Parametric
            return 'wposition'

    elif node.type == 'HAIR_INFO':
        return 'vec3(0.0)' # Tangent Normal

    elif node.type == 'OBJECT_INFO':
        return 'wposition'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[3]: # Location
            return 'vec3(0.0)'
        elif socket == node.outputs[5]: # Velocity
            return 'vec3(0.0)'
        elif socket == node.outputs[6]: # Angular Velocity
            return 'vec3(0.0)'

    elif node.type == 'TANGENT':
        return 'vec3(0.0)'

    elif node.type == 'TEX_COORD':
        #obj = node.object
        #dupli = node.from_dupli
        if socket == node.outputs[0]: # Generated
            return 'vec2(0.0)'
        elif socket == node.outputs[1]: # Normal
            return 'vec2(0.0)'
        elif socket == node.outputs[2]: # UV
            return 'vec2(0.0)'
        elif socket == node.outputs[3]: # Object
            return 'vec2(0.0)'
        elif socket == node.outputs[4]: # Camera
            return 'vec2(0.0)'
        elif socket == node.outputs[5]: # Window
            return 'vec2(0.0)'
        elif socket == node.outputs[6]: # Reflection
            return 'vec2(0.0)'

    elif node.type == 'UVMAP':
        #map = node.uv_map
        #dupli = node.from_dupli
        return 'vec2(0.0)'

    elif node.type == 'BUMP':
        #invert = node.invert
        # strength = parse_value_input(node.inputs[0])
        # distance = parse_value_input(node.inputs[1])
        # height = parse_value_input(node.inputs[2])
        # nor = parse_vector_input(node.inputs[3])
        return 'vec3(0.0)'

    elif node.type == 'MAPPING':
        # vector = parse_vector_input(node.inputs[0])
        return 'vec3(0.0)'

    elif node.type == 'NORMAL':
        if socket == node.outputs[0]:
            return tovec3(node.outputs[0].default_value)
        elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
            nor = parse_vector_input(node.inputs[0])
            return 'vec3(dot({0}, {1}))'.format(tovec3(node.outputs[0].default_value), nor)

    elif node.type == 'NORMAL_MAP':
        #space = node.space
        #map = node.uv_map
        # strength = parse_value_input(node.inputs[0])
        # color = parse_vector_input(node.inputs[1])
        return 'vec3(0.0)'

    elif node.type == 'CURVE_VEC':
        # fac = parse_value_input(node.inputs[0])
        # Pass throuh
        return parse_vector_input(node.inputs[1])

    elif node.type == 'VECT_TRANSFORM':
        #type = node.vector_type
        #conv_from = node.convert_from
        #conv_to = node.convert_to
        # Pass throuh
        return parse_vector_input(node.inputs[0])

    elif node.type == 'COMBXYZ':
        x = parse_value_input(node.inputs[0])
        y = parse_value_input(node.inputs[1])
        z = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(x, y, z)

    elif node.type == 'VECT_MATH':
        vec1 = parse_vector_input(node.inputs[0])
        vec2 = parse_vector_input(node.inputs[1])
        op = node.operation
        if op == 'ADD':
            return '({0} + {1})'.format(vec1, vec2)
        elif op == 'SUBTRACT':
            return '({0} - {1})'.format(vec1, vec2)
        elif op == 'AVERAGE':
            return '(({0} + {1}) / 2.0)'.format(vec1, vec2)
        elif op == 'DOT_PRODUCT':
            return 'vec3(dot({0}, {1}))'.format(vec1, vec2)
        elif op == 'CROSS_PRODUCT':
            return 'cross({0}, {1})'.format(vec1, vec2)
        elif op == 'NORMALIZE':
            return 'normalize({0})'.format(vec1)

def parse_value_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_value_input(l.from_node.inputs[0])

        res_var = write_result(l)
        st = l.from_socket.type        
        if st == 'RGB' or st == 'RGBA' or st == 'VECTOR':
            return '{0}.x'.format(res_var)
        else: # VALUE
            return res_var
    else:
        return tovec1(inp.default_value)

def parse_value(node, socket):

    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Fac
        return '1.0'

    elif node.type == 'CAMERA':
        # View Z Depth
        if socket == node.outputs[1]:
            return 'gl_FragCoord.z'
        # View Distance
        else:
            return 'length(eyeDir)'

    elif node.type == 'FRESNEL':
        ior = parse_value_input(node.inputs[0])
        #nor = parse_vectorZ_input(node.inputs[1])
        return 'pow(1.0 - dotNV, 7.25 / {0})'.format(ior) # max(dotNV, 0.0)

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[6]: # Backfacing
            return '0.0'
        elif socket == node.outputs[7]: # Pointiness
            return '0.0'

    elif node.type == 'HAIR_INFO':
        # Is Strand
        # Intercept
        # Thickness
        pass

    elif node.type == 'LAYER_WEIGHT':
        blend = parse_value_input(node.inputs[0])
        # nor = parse_vector_input(node.inputs[1])
        if socket == node.outputs[0]: # Fresnel
            return 'clamp(pow(1.0 - dotNV, (1.0 - {0}) * 10.0), 0.0, 1.0)'.format(blend)
        elif socket == node.outputs[1]: # Facing
            return '((1.0 - dotNV) * {0})'.format(blend)

    elif node.type == 'LIGHT_PATH':
        if socket == node.outputs[0]: # Is Camera Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Shadow Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Diffuse Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Glossy Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Singular Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Reflection Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Transmission Ray
            return '0.0'
        elif socket == node.outputs[0]: # Ray Length
            return '0.0'
        elif socket == node.outputs[0]: # Ray Depth
            return '0.0'
        elif socket == node.outputs[0]: # Transparent Depth
            return '0.0'
        elif socket == node.outputs[0]: # Transmission Depth
            return '0.0'

    elif node.type == 'OBJECT_INFO':
        if socket == node.outputs[0]: # Object Index
            return '0.0'
        elif socket == node.outputs[0]: # Material Index
            return '0.0'
        elif socket == node.outputs[0]: # Random
            return '0.0'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[0]: # Index
            return '0.0'
        elif socket == node.outputs[1]: # Age
            return '0.0'
        elif socket == node.outputs[2]: # Lifetime
            return '0.0'
        elif socket == node.outputs[4]: # Size
            return '0.0'

    elif node.type == 'VALUE':
        return tovec1(node.outputs[0].default_value)

    elif node.type == 'WIREFRAME':
        #node.use_pixel_size
        # size = parse_value_input(node.inputs[0])
        return '0.0'

    elif node.type == 'TEX_BRICK':
        return '0.0'

    elif node.type == 'TEX_CHECKER':
        # TODO: do not recompute when color socket is also connected
        frag.add_function(str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        return 'tex_checker({0}, {1}, {2}, {3}).r'.format(co, col1, col2, scale)

    elif node.type == 'TEX_GRADIENT':
        return '0.0'

    elif node.type == 'TEX_IMAGE':
        return '0.0'

    elif node.type == 'TEX_MAGIC':
        return '0.0'

    elif node.type == 'TEX_MUSGRAVE':
        # Fall back to noise
        frag.add_function(str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'tex_noise_f({0} * {1})'.format(co, scale)

    elif node.type == 'TEX_NOISE':
        frag.add_function(str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'tex_noise({0} * {1})'.format(co, scale)

    elif node.type == 'TEX_POINTDENSITY':
        return '0.0'

    elif node.type == 'TEX_VORONOI':
        frag.add_function(str_tex_voronoi)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            return 'tex_voronoi({0} * {1}).a'.format(co, scale)
        else: # CELLS
            return 'tex_voronoi({0} * {1}).r'.format(co, scale)

    elif node.type == 'TEX_WAVE':
        return '0.0'

    elif node.type == 'LIGHT_FALLOFF':
        return '0.0'

    elif node.type == 'NORMAL':
        nor = parse_vector_input(node.inputs[0])
        return 'dot({0}, {1})'.format(tovec3(node.outputs[0].default_value), nor)

    elif node.type == 'VALTORGB': # ColorRamp
        return '1.0'

    elif node.type == 'MATH':
        val1 = parse_value_input(node.inputs[0])
        val2 = parse_value_input(node.inputs[1])
        op = node.operation
        if op == 'ADD':
            out_val = '({0} + {1})'.format(val1, val2)
        elif op == 'SUBTRACT':
            out_val = '({0} - {1})'.format(val1, val2)
        elif op == 'MULTIPLY':
            out_val = '({0} * {1})'.format(val1, val2)
        elif op == 'DIVIDE':
            out_val = '({0} / {1})'.format(val1, val2)
        elif op == 'SINE':
            out_val = 'sin({0})'.format(val1)
        elif op == 'COSINE':
            out_val = 'cos({0})'.format(val1)
        elif op == 'TANGENT':
            out_val = 'tan({0})'.format(val1)
        elif op == 'ARCSINE':
            out_val = 'asin({0})'.format(val1)
        elif op == 'ARCCOSINE':
            out_val = 'acos({0})'.format(val1)
        elif op == 'ARCTANGENT':
            out_val = 'atan({0})'.format(val1)
        elif op == 'POWER':
            out_val = 'pow({0}, {1})'.format(val1, val2)
        elif op == 'LOGARITHM':
            out_val = 'log({0})'.format(val1)
        elif op == 'MINIMUM':
            out_val = 'min({0}, {1})'.format(val1, val2)
        elif op == 'MAXIMUM':
            out_val = 'max({0}, {1})'.format(val1, val2)
        elif op == 'ROUND':
            # out_val = 'round({0})'.format(val1)
            out_val = 'floor({0} + 0.5)'.format(val1)
        elif op == 'LESS_THAN':
            out_val = 'float({0} < {1})'.format(val1, val2)
        elif op == 'GREATER_THAN':
            out_val = 'float({0} > {1})'.format(val1, val2)
        elif op == 'MODULO':
            # out_val = 'float({0} % {1})'.format(val1, val2)
            out_val = 'mod({0}, {1})'.format(val1, val2)
        elif op == 'ABSOLUTE':
            out_val = 'abs({0})'.format(val1)
        if node.use_clamp:
            return 'clamp({0}, 0.0, 1.0)'.format(out_val)
        else:
            return out_val

    elif node.type == 'RGBTOBW':
        col = parse_vector_input(node.inputs[0])
        return '((({0}.r * 0.3 + {0}.g * 0.59 + {0}.b * 0.11) / 3.0) * 2.5)'.format(col)

    elif node.type == 'SEPHSV':
        return '0.0'

    elif node.type == 'SEPRGB':
        col = parse_vector_input(node.inputs[0])
        if socket == node.outputs[0]:
            return '{0}.r'.format(col)
        elif socket == node.outputs[1]:
            return '{0}.g'.format(col)
        elif socket == node.outputs[2]:
            return '{0}.b'.format(col)

    elif node.type == 'SEPXYZ':
        vec = parse_vector_input(node.inputs[0])
        if socket == node.outputs[0]:
            return '{0}.x'.format(vec)
        elif socket == node.outputs[1]:
            return '{0}.y'.format(vec)
        elif socket == node.outputs[2]:
            return '{0}.z'.format(vec)

    elif node.type == 'VECT_MATH':
        vec1 = parse_vector_input(node.inputs[0])
        vec2 = parse_vector_input(node.inputs[1])
        op = node.operation
        if op == 'DOT_PRODUCT':
            return 'dot({0}, {1})'.format(vec1, vec2)
        else:
            return '0.0'

def tovec1(v):
    return str(v)

def tovec2(v):
    return 'vec2({0}, {1})'.format(v[0], v[1])

def tovec3(v):
    return 'vec3({0}, {1}, {2})'.format(v[0], v[1], v[2])

def tovec4(v):
    return 'vec4({0}, {1}, {2}, {3})'.format(v[0], v[1], v[2], v[3])

def node_by_type(nodes, ntype):
    for n in nodes:
        if n.type == ntype:
            return n

def socket_index(node, socket):
    for i in range(0, len(node.outputs)):
        if node.outputs[i] == socket:
            return i

def node_name(s):
    s = armutils.safe_source_name(s)
    if len(parents) > 0:
        s = armutils.safe_source_name(parents[-1].name) + '_' + s
    return s

def socket_name(s):
    return armutils.safe_source_name(s)
